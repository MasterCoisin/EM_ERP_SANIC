import datetime
import time

from loguru import logger
from motor.motor_asyncio import AsyncIOMotorCollection
from sanic import Sanic

from apps.purchase_orders.tools import create_1688_order_auto
from apps.shop.tool import get_shop_1688_token
from apps.sku_inventory_detail.tool import inbound, change_sku_inbound_info
from config.constant import APP_NAME, TIP_TO_SELLER
from models.base import BaseMongoModel
from models.order_manager import OrderManager
from models.product import Product
from models.supplier import Supplier
from utils.common import get_purchase_order_id, get_1688_product_id, get_today_time_int

app = Sanic.get_app(APP_NAME)


class PurchaseOrders(BaseMongoModel):
    collection_name = "purchase_orders"

    def __init__(self):
        self.__purchaseOrderId = None
        self.__status = None
        self.__orders = None
        self.__createTime = None
        self.__updateTime = None
        self.__deleted = None

    @property
    def purchaseOrderId(self):
        return self.__purchaseOrderId

    @purchaseOrderId.setter
    def purchaseOrderId(self, value):
        self.__purchaseOrderId = value

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        self.__status = value

    @property
    def orders(self):
        return self.__orders

    @orders.setter
    def orders(self, value):
        self.__orders = value

    @property
    def createTime(self):
        return self.__createTime

    @createTime.setter
    def createTime(self, value):
        self.__createTime = value

    @property
    def updateTime(self):
        return self.__updateTime

    @updateTime.setter
    def updateTime(self, value):
        self.__updateTime = value

    @property
    def deleted(self):
        return self.__deleted

    @deleted.setter
    def deleted(self, value):
        self.__deleted = value

    def to_dict(self):
        return {
            'purchaseOrderId': self.__purchaseOrderId,
            'status': self.__status,
            'orders': self.__orders,
            'createTime': self.__createTime,
            'updateTime': self.__updateTime,
            'deleted': self.__deleted,
        }

    @classmethod
    async def delete(cls, purchase_order_id,campany_id):
        try:
            collection: AsyncIOMotorCollection = app.ctx.mongo[cls.collection_name]
            result = await collection.delete_many({"purchaseOrderId": purchase_order_id, 'status': {'$in': [0, 1]},"campanyId":campany_id})
            print(result)
            return True
        except:
            return False

    @classmethod
    async def create_purchase_order(cls, skus,campany_id):
        try:
            orders = {}
            #
            collection_product: AsyncIOMotorCollection = app.ctx.mongo[Product.collection_name]
            collection_supplier: AsyncIOMotorCollection = app.ctx.mongo[Supplier.collection_name]
            collection_purchase_orders: AsyncIOMotorCollection = app.ctx.mongo[cls.collection_name]
            for sku in skus:
                sku_obj = await collection_product.find_one({"sku": sku["sku"], 'deleted': False})
                if not sku_obj:
                    return False, "sku未找到", None
                images = sku_obj.get("images", [])
                product_name = sku_obj.get("productName", None)
                supplier_info = sku_obj.get("supplierInfo", {})
                price = supplier_info.get("purchaseCost", None)
                try:
                    price = float(price)
                except:
                    pass
                supplier_uuid = supplier_info["supplierId"]
                product_url = sku_obj["url1688"]
                spec_id = supplier_info["specId"]
                sku_data = {"sku": sku["sku"], "productName": product_name, "count": int(sku["count"]),"skuBatchNumber":int(time.time()),
                            "images": images,
                            "productUrl": product_url, "specId": spec_id, "purchaseCost": price, "fee": None,
                            "offerId": spec_id["offer_id"] if spec_id.get("offer_id", None) else get_1688_product_id(
                                product_url),
                            "inboundCount": None,
                            "inboundWarehouseId": None, "deleted": False}
                if supplier_uuid not in orders:
                    obj_supplier = await collection_supplier.find_one({"uuid": supplier_uuid}, {"uuid": 1, "name": 1})
                    orders[supplier_uuid] = {"supplier": {
                        "uuid": obj_supplier.get("uuid", None),
                        "name": obj_supplier.get("name", None),
                    }, "skus": [],
                        "order_info": {"status": 0, "order_id": None,
                                       "order_info_onsubmit_order": {"totalSuccessAmount": None,
                                                                     "orderId": None, "postFee": None},
                                       "order_info": {},
                                       "tip_for_seller": TIP_TO_SELLER}, "deleted": False}
                orders[supplier_uuid]["skus"].append(sku_data)
            purchase_order_id = get_purchase_order_id()
            await collection_purchase_orders.insert_one({
                "campanyId":campany_id,
                "purchaseOrderId": purchase_order_id,
                "status": 0,
                "orders": orders,
                "createTime": datetime.datetime.now(),
                "updateTime": datetime.datetime.now(),
                "deleted": False
            })
            return True, "OK", purchase_order_id
        except Exception as e:
            logger.exception(e)
            return False, "系统出错", None

    @classmethod
    async def delete_supplier(cls, purchase_order_id, supplier_uuid,campany_id):
        try:
            collection_purchase_orders: AsyncIOMotorCollection = app.ctx.mongo[cls.collection_name]
            result = await collection_purchase_orders.find_one({"purchaseOrderId": purchase_order_id,"campanyId":campany_id})
            if not result:
                return False
            orders = result.get("orders", {})
            if supplier_uuid not in orders:
                return False
            if orders[supplier_uuid].get("order_info", {}).get("status", 0) not in [0, 1]:
                return False
            orders[supplier_uuid]["deleted"] = True
            no_has_order_ = True
            for i in orders.values():
                if not i["deleted"]:
                    no_has_order_ = False
            await collection_purchase_orders.update_one({"purchaseOrderId": purchase_order_id,"campanyId":campany_id},
                                                        {"$set": {"orders": orders, "deleted": no_has_order_}})
            return True
        except:
            return False

    @classmethod
    async def change_status_fapiao(cls, purchase_order_id, supplier_uuid, has_fapiao, has_kaipiao, has_print_fapiao,campany_id):
        try:
            collection: AsyncIOMotorCollection = app.ctx.mongo[cls.collection_name]
            result = await collection.find_one({"purchaseOrderId": purchase_order_id,"campanyId":campany_id})
            if not result:
                return False
            orders = result.get("orders", {})
            if supplier_uuid not in orders:
                return False
            orders[supplier_uuid]["order_info"]["has_fapiao"] = has_fapiao
            orders[supplier_uuid]["order_info"]["has_kaipiao"] = has_kaipiao
            orders[supplier_uuid]["order_info"]["has_print_fapiao"] = has_print_fapiao
            await collection.update_one({"purchaseOrderId": purchase_order_id,"campanyId":campany_id},
                                        {"$set": {"orders": orders}})
            return True
        except Exception as e:
            logger.exception(e)
            return False

    @classmethod
    async def add_new_1688_order(cls, data):
        collection_order_manager: AsyncIOMotorCollection = app.ctx.mongo[OrderManager.collection_name]
        data["createTime"] = datetime.datetime.now()
        data["updateTime"] = datetime.datetime.now()
        document = await collection_order_manager.count_documents(
            filter={f: {"$eq": data[f]} for f in ["orderId", "supplierUuid", "purchaseOrderId"]})
        if not document:
            await collection_order_manager.insert_one(data)

    @classmethod
    async def create_order_auto(cls, supplier_uuid, address_id, tip_for_seller, purchase_order_id, shop_id,campany_id):
        try:
            collection_purchase_orders: AsyncIOMotorCollection = app.ctx.mongo[cls.collection_name]
            result = await collection_purchase_orders.find_one({"purchaseOrderId": purchase_order_id, "deleted": False,"campanyId":campany_id})
            if not result:
                return False, "采购单不存在或未激活"
            orders = result.get("orders", {})
            if supplier_uuid not in orders or orders[supplier_uuid]["deleted"]:
                return False, "采购单不存在该供应商订单"
            if orders[supplier_uuid]["order_info"]["status"] != 0:
                return False, "下单失败，请刷新页面看看!"
            # 下单数据准备
            skus_data = orders[supplier_uuid]["skus"]
            skus_data = [{"specId": sku_["specId"], "count": int(sku_["count"]), "offerId": int(sku_["offerId"])} for
                         sku_ in skus_data]
            # 获取店铺token
            token = await get_shop_1688_token(shop_id=shop_id)
            resp = await create_1688_order_auto(address_id=address_id, skus_data=skus_data,
                                                tip_for_seller=tip_for_seller, token=token)
            if resp.get("success", False):
                orders[supplier_uuid]["shopId"] = shop_id
                orders[supplier_uuid]["order_info"]["order_id"] = resp.get("result", {}).get("orderId", None)
                orders[supplier_uuid]["order_info"]["order_info_onsubmit_order"] = resp.get("result", {})
                orders[supplier_uuid]["order_info"]["status"] = 1
                orders[supplier_uuid]["order_info"]["tip_for_seller"] = tip_for_seller
                orders[supplier_uuid]["addressId"] = address_id
                orders[supplier_uuid]["is1688"] = True
                await collection_purchase_orders.update_one({"purchaseOrderId": purchase_order_id,"campanyId":campany_id},
                                                            {"$set": {"orders": orders}})
                # 存入订单表
                await cls.add_new_1688_order({
                    "campanyId": campany_id,
                    "orderId": resp.get("result", {}).get("orderId", None),
                    "supplierUuid": supplier_uuid,
                    "purchaseOrderId": purchase_order_id,
                    "status": 1,
                    "tradeInfo": {},
                })
                return True, "OK"
            return False, str(resp)
        except Exception as e:
            logger.exception(e)
            return False, "系统出错"

    @classmethod
    async def create_order_not_1688(cls, supplier_uuid, purchase_order_id, skus, shop_id,campany_id):
        try:
            collection_purchase_orders: AsyncIOMotorCollection = app.ctx.mongo[cls.collection_name]
            result = await collection_purchase_orders.find_one({"purchaseOrderId": purchase_order_id, "deleted": False,"campanyId":campany_id})
            if not result:
                return False, "采购单不存在或未激活"
            orders = result.get("orders", {})
            if supplier_uuid not in orders or orders[supplier_uuid]["deleted"]:
                return False, "采购单不存在该供应商订单"
            if orders[supplier_uuid]["order_info"]["status"] != 0:
                return False, "下单失败，请刷新页面看看!"
            # 下单数据准备
            skus_data = orders[supplier_uuid]["skus"]
            totalSuccessAmount = 0
            for s in skus_data:
                fee = int(float(skus.get(s["sku"], None)) * 100)
                s["fee"] = fee
                totalSuccessAmount += fee
            orders[supplier_uuid]["shopId"] = shop_id
            orders[supplier_uuid]["order_info"]["order_info_onsubmit_order"]["totalSuccessAmount"] = totalSuccessAmount
            orders[supplier_uuid]["order_info"]["status"] = 1
            orders[supplier_uuid]["is1688"] = False
            await collection_purchase_orders.update_one({"purchaseOrderId": purchase_order_id,"campanyId":campany_id},
                                                        {"$set": {"orders": orders}})
            return True, "OK"
        except Exception as e:
            logger.exception(e)
            return False, "系统出错"

    @classmethod
    async def change_status_not_1688(cls, supplier_uuid, purchase_order_id, shop_id,campany_id,status):
        try:
            collection_purchase_orders: AsyncIOMotorCollection = app.ctx.mongo[cls.collection_name]
            result = await collection_purchase_orders.find_one({"purchaseOrderId": purchase_order_id, "deleted": False,"campanyId":campany_id})
            if not result:
                return False, "采购单不存在或未激活"
            orders = result.get("orders", {})
            if supplier_uuid not in orders or orders[supplier_uuid]["deleted"]:
                return False, "采购单不存在该供应商订单"
            if orders[supplier_uuid]["order_info"]["status"] >=status:
                return False, "状态更新失败，请刷新页面看看!"
            # 下单数据准备
            orders[supplier_uuid]["order_info"]["status"] = status
            await collection_purchase_orders.update_one({"purchaseOrderId": purchase_order_id,"campanyId":campany_id},
                                                        {"$set": {"orders": orders}})
            return True, "OK"
        except Exception as e:
            logger.exception(e)
            return False, "系统出错"

    @classmethod
    async def inbound(cls,supplier_uuid, purchase_order_id, skus, campany_id):
        try:
            collection_purchase_orders: AsyncIOMotorCollection = app.ctx.mongo[cls.collection_name]
            result = await collection_purchase_orders.find_one(
                {"purchaseOrderId": purchase_order_id, "deleted": False, "campanyId": campany_id})
            if not result:
                return False, "采购单不存在或未激活"
            orders = result.get("orders", {})
            if supplier_uuid not in orders or orders[supplier_uuid]["deleted"]:
                return False, "采购单不存在该供应商订单"
            if orders[supplier_uuid]["order_info"]["status"] > 8:
                return False, "状态更新失败，请刷新页面看看!"
            # 更新sku入库数量
            for sku_info in orders[supplier_uuid]["skus"]:
                if sku_info["sku"] in skus:
                    sku_info["inboundCount"] = skus[sku_info["sku"]]["inboundCount"]
                    sku_info["inboundWarehouseId"] = skus[sku_info["sku"]]["inboundWarehouseId"]
                    skus[sku_info["sku"]]["fee"] = sku_info["fee"]
                    skus[sku_info["sku"]]["skuBatchNumber"] = sku_info.get("skuBatchNumber",int(time.time()))
            # 入库
            await inbound(skus,campany_id)
            # 入库完成
            orders[supplier_uuid]["order_info"]["status"] = 8

            await collection_purchase_orders.update_one({"purchaseOrderId": purchase_order_id, "campanyId": campany_id},
                                                        {"$set": {"orders": orders}})
            return True, "OK"
        except Exception as e:
            logger.exception(e)
            return False, "系统出错"

    @classmethod
    async def change_inbound_info(cls,supplier_uuid, purchase_order_id, skus, campany_id):
        try:
            collection_purchase_orders: AsyncIOMotorCollection = app.ctx.mongo[cls.collection_name]
            result = await collection_purchase_orders.find_one(
                {"purchaseOrderId": purchase_order_id, "deleted": False, "campanyId": campany_id})
            if not result:
                return False, "采购单不存在或未激活"
            orders = result.get("orders", {})
            if supplier_uuid not in orders or orders[supplier_uuid]["deleted"]:
                return False, "采购单不存在该供应商订单"
            if orders[supplier_uuid]["order_info"]["status"] > 8:
                return False, "状态更新失败，请刷新页面看看!"
            # 更新sku入库数量
            for sku_info in orders[supplier_uuid]["skus"]:
                if sku_info["sku"] in skus:
                    sku = sku_info["sku"]
                    skuBatchNumber = sku_info["skuBatchNumber"]
                    inboundWarehouseId = sku_info["inboundWarehouseId"]
                    oldInboundCount = sku_info["inboundCount"]
                    oldFee = sku_info["fee"]
                    newInboundCount = skus[sku_info["sku"]]["inboundCount"]
                    newFee = skus[sku_info["sku"]]["fee"]
                    if oldInboundCount!=newInboundCount or oldFee!=newFee:
                        await change_sku_inbound_info(campany_id,sku,inboundWarehouseId,oldInboundCount,oldFee,newInboundCount,newFee,skuBatchNumber)
                        sku_info["inboundCount"] = newInboundCount
                        sku_info["fee"] = skus[sku_info["sku"]]["fee"]
            await collection_purchase_orders.update_one({"purchaseOrderId": purchase_order_id, "campanyId": campany_id},
                                                        {"$set": {"orders": orders}})
            return True, "OK"
        except Exception as e:
            logger.exception(e)
            return False, "系统出错"

    @classmethod
    async def check_status_and_update(cls,purchase_order_id, campany_id):
        try:
            collection_purchase_orders: AsyncIOMotorCollection = app.ctx.mongo[cls.collection_name]
            result = await collection_purchase_orders.find_one(
                {"purchaseOrderId": purchase_order_id, "deleted": False, "campanyId": campany_id})
            if not result:
                return False, "采购单不存在或未激活"
            orders = result.get("orders", {})
            has_finished = True
            has_sign = True
            has_sure = True
            for supplier_uuid,v in orders.items():
                if orders[supplier_uuid]["order_info"]["status"]!=8:
                    has_finished = False
                if orders[supplier_uuid]["order_info"]["status"]<7:
                    has_sign = False
                if orders[supplier_uuid]["order_info"]["status"]<1:
                    has_sure = False
            if has_finished:
                await collection_purchase_orders.update_one(
                    {"purchaseOrderId": purchase_order_id, "deleted": False, "campanyId": campany_id},{"$set":{"status":4}})
            elif has_sign:
                await collection_purchase_orders.update_one(
                    {"purchaseOrderId": purchase_order_id, "deleted": False, "campanyId": campany_id},
                    {"$set": {"status": 3}})
            elif has_sure:
                await collection_purchase_orders.update_one(
                    {"purchaseOrderId": purchase_order_id, "deleted": False, "campanyId": campany_id},
                    {"$set": {"status": 2}})

        except Exception as e:
            logger.exception(e)
            return False, "系统出错"