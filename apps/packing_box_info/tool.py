# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：tool.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-04-18 15:05 
-------------------------------------
'''
import datetime

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import UpdateOne
from sanic import Sanic
from loguru import logger

from file_creatoer.yf_tempalte import form_tempalte_pc, form_tempalte_ynd
from models.em_reception import EmReception
from models.sku_inventory_detail import SkuInventoryDetail
from models.sku_inventory_index import SkuInventoryIndex
from apps.listing.tool import get_packing_data_by_ean, get_sku_data_by_ean, get_listing_shipping_info
from config.constant import APP_NAME
from models.packing_box_info import PackingBoxInfo
from utils.common import get_uuid

app = Sanic.get_app(APP_NAME)


async def get_packing_box_info(packing_order_id, campany_id):
    collection: AsyncIOMotorCollection = app.ctx.mongo[PackingBoxInfo.collection_name]
    result = await collection.find_one({"packingOrderId": packing_order_id, "campanyId": campany_id}, {"_id": 0})
    return result


async def init_packing_summary_ean_info(packing_info, campany_id):
    res = {}
    for box in packing_info:
        for ean, count in box.get("mskuInBox", {}).items():
            res[ean] = res.get(ean, 0) + count
    result = {}
    for ean, count in res.items():
        is_ok, data = await get_packing_data_by_ean(ean, campany_id)
        if is_ok:
            data["count"] = count
            result[ean] = data
    return result


async def check_packing_info_version(packing_order_id, campany_id, version):
    collection: AsyncIOMotorCollection = app.ctx.mongo[PackingBoxInfo.collection_name]
    result = await collection.find_one({"packingOrderId": packing_order_id, "campanyId": campany_id},
                                       {"_id": 0, "version": 1})
    if not version:
        return False, "存在新版本，即将刷新界面", True
    if not result:
        return False, "装箱单不存在", True
    else:
        if result.get("version", 0) > version:
            return False, "存在新版本，即将刷新界面", True
        else:
            return True, "OK", False


async def add_box_in_packing_info(packing_order_id, campany_id, new_box_item):
    collection: AsyncIOMotorCollection = app.ctx.mongo[PackingBoxInfo.collection_name]
    try:
        # 使用 $push 操作符将 new_box_item 添加到 packingInfo 列表中
        result = await collection.update_one(
            {
                "packingOrderId": packing_order_id,
                "campanyId": campany_id
            },
            {
                "$push": {
                    "packingInfo": new_box_item
                }
            },
            upsert=False  # 如果文档不存在，不插入新文档
        )
        if result.modified_count > 0:
            return True
        else:
            return False
    except Exception as e:
        logger.exception(e)
        return False


async def delete_box_in_packing_info(packing_order_id, campany_id, box_index):
    collection: AsyncIOMotorCollection = app.ctx.mongo[PackingBoxInfo.collection_name]
    try:
        # 使用 $push 操作符将 new_box_item 添加到 packingInfo 列表中
        result = await collection.find_one({
            "packingOrderId": packing_order_id,
            "campanyId": campany_id
        })
        if result and len(result.get("packingInfo", [])) > box_index:
            packing_info_new = result.get("packingInfo", [])
            for ean,count in packing_info_new[box_index].get("mskuInBox",{}).items():
                await remove_ean_packing_info(packing_order_id, campany_id, box_index, ean, count, result.get("whId",None))
            del packing_info_new[box_index]
            result = await collection.update_one(
                {
                    "packingOrderId": packing_order_id,
                    "campanyId": campany_id
                },
                {
                    "$set": {
                        "packingInfo": packing_info_new
                    }
                },
                upsert=False  # 如果文档不存在，不插入新文档
            )
            if result.modified_count > 0:
                return True
            else:
                return False
        else:
            return False
    except Exception as e:
        logger.exception(e)
        return False


async def add_ean_in_packing_info(packing_order_id, campany_id, box_index, ean, count, whId):
    collection: AsyncIOMotorCollection = app.ctx.mongo[PackingBoxInfo.collection_name]
    collection_sku_inventory_detail: AsyncIOMotorCollection = app.ctx.mongo[SkuInventoryDetail.collection_name]
    collection_sku_inventory_index: AsyncIOMotorCollection = app.ctx.mongo[SkuInventoryIndex.collection_name]
    try:
        # 使用 $push 操作符将 new_box_item 添加到 packingInfo 列表中
        result = await collection.find_one({
            "packingOrderId": packing_order_id,
            "campanyId": campany_id
        })
        if result and len(result.get("packingInfo", [])) > box_index:
            # 判断sku数量是否足够装箱
            is_ok, sku_data = await get_sku_data_by_ean(ean, campany_id)
            if not is_ok:
                return False, "添加失败"
            for sku_info in sku_data:
                sku_count = await collection_sku_inventory_detail.count_documents(
                    {"campanyId": campany_id, "whId": whId, "sku": sku_info["sku"], "skuStatus": 0})
                if sku_count < count * sku_info["count"]:
                    return False, "仓库库存不足"
            for sku_info in sku_data:
                cursor = collection_sku_inventory_detail.find({
                    "campanyId": campany_id,
                    "whId": whId,
                    "sku": sku_info["sku"], "skuStatus": 0
                }).sort([
                    ("skuBatchNumber", 1),
                    ("skuBatchOrder", 1)
                ]).limit(count * sku_info["count"])
                # 构建批量更新操作列表
                update_operations = []
                async for doc in cursor:
                    update_operations.append(
                        UpdateOne(
                            {"_id": doc["_id"]},
                            {"$set": {"skuStatus": 1, "packingOrderId": packing_order_id,"toEan":ean}}
                        )
                    )
                # 执行批量更新操作
                if update_operations:
                    await collection_sku_inventory_detail.bulk_write(update_operations)
                # 更新index
                await collection_sku_inventory_index.update_one({
                    "campanyId": campany_id,
                    "whId": whId,
                    "sku": sku_info["sku"]
                }, {
                    "$inc": {
                        "skuInBox": count * sku_info["count"],
                        "skuLeft": -count * sku_info["count"]
                    }
                })
            # 更新装箱数据
            packing_info_new = result.get("packingInfo", [{}])
            packing_info_new[box_index]["mskuInBox"][ean] = packing_info_new[box_index]["mskuInBox"].get(ean,
                                                                                                         0) + count
            result = await collection.update_one(
                {
                    "packingOrderId": packing_order_id,
                    "campanyId": campany_id
                },
                {
                    "$set": {
                        "packingInfo": packing_info_new
                    }
                },
                upsert=False  # 如果文档不存在，不插入新文档
            )
            if result.modified_count > 0:
                return True, "OK"
            else:
                return False, "添加失败"
        else:
            return False, "添加失败"
    except Exception as e:
        logger.exception(e)
        return False, "添加失败"


async def remove_ean_packing_info(packing_order_id, campany_id, box_index, ean, count, whId):
    collection: AsyncIOMotorCollection = app.ctx.mongo[PackingBoxInfo.collection_name]
    collection_sku_inventory_detail: AsyncIOMotorCollection = app.ctx.mongo[SkuInventoryDetail.collection_name]
    collection_sku_inventory_index: AsyncIOMotorCollection = app.ctx.mongo[SkuInventoryIndex.collection_name]
    try:
        result = await collection.find_one({
            "packingOrderId": packing_order_id,
            "campanyId": campany_id
        })
        if result and len(result.get("packingInfo", [])) > box_index:
            # 处理sku库存
            is_ok, sku_data = await get_sku_data_by_ean(ean, campany_id)
            if not is_ok:
                return False, "添加失败"
            for sku_info in sku_data:
                sku_count = await collection_sku_inventory_detail.count_documents(
                    {"campanyId": campany_id, "whId": whId, "sku": sku_info["sku"], "skuStatus": 1,
                     "packingOrderId": packing_order_id})
                if sku_count < count * sku_info["count"]:
                    return False, "库存错误"
            for sku_info in sku_data:
                cursor = collection_sku_inventory_detail.find({
                    "campanyId": campany_id,
                    "whId": whId,
                    "sku": sku_info["sku"], "skuStatus": 1, "packingOrderId": packing_order_id
                }).sort([
                    ("skuBatchNumber", 1),
                    ("skuBatchOrder", 1)
                ]).limit(count * sku_info["count"])
                # 构建批量更新操作列表
                update_operations = []
                async for doc in cursor:
                    update_operations.append(
                        UpdateOne(
                            {"_id": doc["_id"]},
                            {"$set": {"skuStatus": 0, "packingOrderId": None,"toEan":None}}
                        )
                    )
                # 执行批量更新操作
                if update_operations:
                    await collection_sku_inventory_detail.bulk_write(update_operations)
                # 更新index
                await collection_sku_inventory_index.update_one({
                    "campanyId": campany_id,
                    "whId": whId,
                    "sku": sku_info["sku"]
                }, {
                    "$inc": {
                        "skuInBox": -count * sku_info["count"],
                        "skuLeft": count * sku_info["count"]
                    }
                })
            #
            packing_info_new = result.get("packingInfo", [{}])
            packing_info_new[box_index]["mskuInBox"][ean] = packing_info_new[box_index]["mskuInBox"].get(ean,
                                                                                                         0) - count
            if packing_info_new[box_index]["mskuInBox"][ean] <= 0:
                del packing_info_new[box_index]["mskuInBox"][ean]
            result = await collection.update_one(
                {
                    "packingOrderId": packing_order_id,
                    "campanyId": campany_id
                },
                {
                    "$set": {
                        "packingInfo": packing_info_new
                    }
                },
                upsert=False  # 如果文档不存在，不插入新文档
            )
            print(result)
            if result.modified_count > 0:
                return True, "OK"
            else:
                return False, "出箱失败"
        else:
            return False, "出箱失败"
    except Exception as e:
        logger.exception(e)
        return False, "出箱失败"


async def create_em_reception_task(packing_order_id, campany_id):
    collection: AsyncIOMotorCollection = app.ctx.mongo[PackingBoxInfo.collection_name]
    collection_em_reception: AsyncIOMotorCollection = app.ctx.mongo[EmReception.collection_name]

    result = await collection.find_one({
        "packingOrderId": packing_order_id,
        "campanyId": campany_id
    })
    if result:
        shop = result.get("shop", None)
        whId = result.get("whId", None)
        packingInfo = result.get("packingInfo", [])
        ean_info = {}
        for box_info in packingInfo:
            for ean, count in box_info.get("mskuInBox", {}).items():
                ean_info[ean] = ean_info.get(ean, 0) + count
        ean_info = [{"ean": ean, "count": count, "uploadStatus": 0} for ean, count in
                    ean_info.items()]  # uploadStatus: 0:未上传 1:上传成功 2:上传失败
        emReceptionId = get_uuid()
        add_data = {
            "campanyId": campany_id,
            "shop": shop,
            "emReceptionId": emReceptionId,
            "packingOrderId": packing_order_id,
            "shipmentsOrderId": None,
            "sendFromWhId": whId,
            "sendToWhId": None,
            "receptionId": None,
            "hasSend": False,
            "eanInfo": ean_info,
            # "productCount": None,
            # "createDone": False,
            "createTime": datetime.datetime.now(),
            "updateTime": datetime.datetime.now(),
            "deleted":False
        }
        await collection.update_one({
            "packingOrderId": packing_order_id,
            "campanyId": campany_id
        },{"$set":{"emReceptionId":emReceptionId}})
        await collection_em_reception.insert_one(add_data)
        return True,{"emReceptionId":emReceptionId}
    else:
        return False, "装箱单未找到"


async def create_yf_template(packing_order_id, campany_id, logistic_providor):
    collection: AsyncIOMotorCollection = app.ctx.mongo[PackingBoxInfo.collection_name]
    data = await collection.find_one({
        "packingOrderId": packing_order_id,
        "campanyId": campany_id
    })
    if data:
        packing_info = data.get("packingInfo",[])
        eans = set()
        for item in packing_info:
            eans |= set(list(item.get("mskuInBox",{})))
        ean_info = {ean:await get_listing_shipping_info(ean) for ean in list(eans)}

        if logistic_providor == 'pc':
            return form_tempalte_pc(packing_info,ean_info)
        elif logistic_providor == 'ynd':
            return form_tempalte_ynd(packing_info,ean_info)
        else:
            return None
