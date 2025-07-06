# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：em_order_deal_to_cal_profit.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：处理订单和库存归因
@Date        ：2025-05-17 22:24 
-------------------------------------
'''
import time
from loguru import logger

from config.constant import EXCHANGE
from utils.format_tool import str_to_datetime
from utils.models import ModelManager
from utils.common import to_mongo


def init_order_queue():
    """
    初始化订单处理队列
    """
    objs = em_orders_model.objects().only("campanyId", "country", "shop", "orderId", "modified")
    add = []
    for obj in objs:
        modified = str_to_datetime(obj.modified)
        add.append({
            "campanyId": obj.campanyId,
            "shop": obj.shop,
            "country": obj.country,
            "orderId": obj.orderId,
            "status": 0,
            "modified": modified
        })
    if add:
        to_mongo(order_modify_queue_model, add, ["campanyId", "shop", "country", "orderId", "modified"])


class OrderDeal():
    SHOP_TO_WHID = {}

    def __init__(self, obj):
        self.obj = obj
        self.campanyId = obj.campanyId
        self.shop = obj.shop
        self.country = obj.country
        self.orderId = obj.orderId
        self.status = obj.status
        self.modified = obj.modified

    def _get_whid_by_shop(self):
        if self.shop not in OrderDeal.SHOP_TO_WHID:
            OrderDeal.SHOP_TO_WHID[self.shop] = overseas_warehouse.objects(campanyId=self.campanyId,
                                                                           shop=self.shop).first().whId
        return OrderDeal.SHOP_TO_WHID[self.shop]

    def _deal_finished(self, em_order_obj, order_create_date, date):
        products = em_order_obj.products
        cost_structure = {

        }
        for product_info in products:
            product_id = int(product_info.get("product_id", None))
            ean = listing_model.objects(**{f"emAttribute__id__{self.country}": product_id}).only("ean").first().ean
            quantity = product_info.get("quantity", 0)
            mskuFee, mskuHeadFee = self._deal_ean_storage(ean=ean, count=quantity, order_create_date=order_create_date,
                                                          date=date)
            if str(product_id) not in cost_structure:
                cost_structure[str(product_id)] = {
                    "mskuFee": mskuFee,
                    "mskuHeadFee": mskuHeadFee
                }
            else:
                cost_structure[str(product_id)]["mskuFee"]+=mskuFee
                cost_structure[str(product_id)]["mskuHeadFee"]+=mskuHeadFee

        em_order_obj.update(costStructure=cost_structure)
        self.obj.update(status=1)

    def _deal_cancel(self, em_order_obj, order_create_date, date):
        products = em_order_obj.products
        cost_structure = {

        }
        for product_info in products:
            product_id = int(product_info.get("product_id", None))
            ean = listing_model.objects(**{f"emAttribute__id__{self.country}": product_id}).only("ean").first().ean
            quantity = 0
            mskuFee, mskuHeadFee = self._deal_ean_storage(ean=ean, count=quantity, order_create_date=order_create_date,
                                                          date=date)
            if str(product_id) not in cost_structure:
                cost_structure[str(product_id)] = {
                    "mskuFee": mskuFee,
                    "mskuHeadFee": mskuHeadFee
                }
            else:
                cost_structure[str(product_id)]["mskuFee"] += mskuFee
                cost_structure[str(product_id)]["mskuHeadFee"] += mskuHeadFee
        em_order_obj.update(costStructure=cost_structure)
        self.obj.update(status=1)

    def _deal_retuen(self, em_order_obj, order_create_date, date):
        products = em_order_obj.products
        cost_structure = {

        }
        for product_info in products:
            product_id = int(product_info.get("product_id", None))
            ean = listing_model.objects(**{f"emAttribute__id__{self.country}": product_id}).only("ean").first().ean
            quantity = product_info.get("quantity", 0)
            mskuFee, mskuHeadFee = self._deal_ean_storage(ean=ean, count=quantity, order_create_date=order_create_date,
                                                          date=date)
            if str(product_id) not in cost_structure:
                cost_structure[str(product_id)] = {
                    "mskuFee": mskuFee,
                    "mskuHeadFee": mskuHeadFee
                }
            else:
                cost_structure[str(product_id)]["mskuFee"] += mskuFee
                cost_structure[str(product_id)]["mskuHeadFee"] += mskuHeadFee
        em_order_obj.update(costStructure=cost_structure)
        self.obj.update(status=1)

    def _deal_ean_storage(self, ean, count, order_create_date, date):
        mskuFee = 0
        mskuHeadFee = 0
        old_count = msku_inventory_detail.objects(campanyId=self.campanyId, whId=self._get_whid_by_shop(),
                                                  buyCountry=self.country, ean=ean, orderId=self.orderId,
                                                  status=1).count()
        if old_count == count:
            # print(self._get_whid_by_shop(), ean, old_count, f"=", count)
            objs = msku_inventory_detail.objects(campanyId=self.campanyId, whId=self._get_whid_by_shop(),
                                                 buyCountry=self.country, ean=ean, orderId=self.orderId).only("mskuFee",
                                                                                                              "mskuHeadFee")
            for obj in objs:
                mskuFee += obj.mskuFee
                mskuHeadFee += obj.mskuHeadFee
                obj.update(orderCreateDate=order_create_date, orderCreateDateTime=date)
        elif old_count > count:
            # print(self._get_whid_by_shop(), ean, old_count, f">", count)
            delta_count = old_count - count
            update_objs = msku_inventory_detail.objects(campanyId=self.campanyId, whId=self._get_whid_by_shop(),
                                                        buyCountry=self.country, ean=ean, orderId=self.orderId,
                                                        status=1).order_by(
                "-mskuBatchNumber", "-mskuBatchOrder").limit(delta_count)
            for u_obj in update_objs:
                u_obj.update(buyCountry=None, orderId=None,
                             statusVersion=None,
                             orderCreateDate=None, orderCreateDateTime=None, status=0)
            # 更新index
            msku_inventory_index_obj = msku_inventory_index.objects(campanyId=self.campanyId,
                                                                    whId=self._get_whid_by_shop(), ean=ean).only(
                "mskuHasPurchased", "mskuLeft").first()
            msku_inventory_index_obj.update(mskuHasPurchased=msku_inventory_index_obj.mskuHasPurchased - delta_count,
                                            mskuLeft=msku_inventory_index_obj.mskuLeft + delta_count)
            #
            objs = msku_inventory_detail.objects(campanyId=self.campanyId, whId=self._get_whid_by_shop(),
                                                 buyCountry=self.country, ean=ean, orderId=self.orderId).only("mskuFee",
                                                                                                              "mskuHeadFee")
            for obj in objs:
                mskuFee += obj.mskuFee
                mskuHeadFee += obj.mskuHeadFee
                obj.update(orderCreateDate=order_create_date, orderCreateDateTime=date)
        else:
            # print(self._get_whid_by_shop(), ean, old_count, f"<", count)
            delta_count = count - old_count
            if msku_inventory_detail.objects(campanyId=self.campanyId, whId=self._get_whid_by_shop(), ean=ean,
                                             status=0).order_by(
                "mskuBatchNumber", "mskuBatchOrder").count() < delta_count:
                raise
            update_objs = msku_inventory_detail.objects(campanyId=self.campanyId, whId=self._get_whid_by_shop(),
                                                        ean=ean, status=0).order_by(
                "mskuBatchNumber", "mskuBatchOrder").limit(delta_count)
            for u_obj in update_objs:
                u_obj.update(buyCountry=self.country,
                             orderId=self.orderId,
                             statusVersion=int(
                                 str(order_create_date)[:6]),
                             orderCreateDate=order_create_date,
                             orderCreateDateTime=date,
                             status=1)
            # 更新index
            msku_inventory_index_obj = msku_inventory_index.objects(campanyId=self.campanyId,
                                                                    whId=self._get_whid_by_shop(), ean=ean).only(
                "mskuHasPurchased", "mskuLeft").first()
            msku_inventory_index_obj.update(mskuHasPurchased=msku_inventory_index_obj.mskuHasPurchased + delta_count,
                                            mskuLeft=msku_inventory_index_obj.mskuLeft - delta_count)

            objs = msku_inventory_detail.objects(campanyId=self.campanyId, whId=self._get_whid_by_shop(),
                                                 buyCountry=self.country, ean=ean, orderId=self.orderId).only("mskuFee",
                                                                                                              "mskuHeadFee")
            for obj in objs:
                mskuFee += obj.mskuFee
                mskuHeadFee += obj.mskuHeadFee
        if mskuFee == 0 and count != 0:
            print(self.orderId)
        return mskuFee, mskuHeadFee

    def run(self):
        if self.shop!='wl':
            return
        # 获取订单数据
        em_order_obj = em_orders_model.objects(campanyId=self.campanyId, shop=self.shop, country=self.country,
                                               orderId=self.orderId).first()
        if not em_order_obj: return
        # 判断订单状态 status 0:取消 4:完成 5:退货
        status = em_order_obj.status  # 订单状态
        date = em_order_obj.date
        order_create_date = int(f"{date.year}{date.month:0>2}{date.day:0>2}")
        # 处理不同状态订单
        if status == 4:
            # 订单完成
            self._deal_finished(em_order_obj, order_create_date, date)
        elif status == 0:
            # 订单取消
            self._deal_cancel(em_order_obj, order_create_date, date)
        elif status == 5:
            # 订单退货
            self._deal_retuen(em_order_obj, order_create_date, date)
        print(status, order_create_date)


def task():
    order_modify_objs = order_modify_queue_model.objects(status=0).order_by("modified").limit(100)
    for obj in order_modify_objs:
        try:
            OrderDeal(obj).run()
        except Exception as e:
            if obj.shop == 'wl':
                logger.exception(e)
            print(f"error,{obj.shop}")
            obj.update(status=-1)
            pass


def main():
    while True:
        task()
        time.sleep(1)


if __name__ == '__main__':
    DEBUG = True
    order_status = {0: "Canceled", 1: "New", 2: "In progress", 3: "Prepared", 4: "Finalized", 5: "Returned"}
    payment_status_dict = {0: "未支付", 1: "已支付"}
    em_orders_model = ModelManager.get_model("em_orders", "base")
    listing_model = ModelManager.get_model("listing", "base")
    overseas_warehouse = ModelManager.get_model("overseas_warehouse", "base")
    order_modify_queue_model = ModelManager.get_model("order_modify_queue", "base")
    msku_inventory_index = ModelManager.get_model("msku_inventory_index", "base")
    msku_inventory_detail = ModelManager.get_model("msku_inventory_detail", "base")
    # init_order_queue()
    main()
