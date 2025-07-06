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
@Date        ：2025-02-11 16:53 
-------------------------------------
'''
import time

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import UpdateOne, DeleteOne
from sanic import Sanic

from apps.listing.tool import get_sku_data_by_ean, get_weighing_info_by_eans
from apps.msku_inventory_detail.tool import change_ean_for_shipments_order, change_ean_for_shipments_order_inbound
from apps.sku_inventory_index.tool import get_full_data_by_sku
from config.constant import APP_NAME
from models.msku_inventory_detail import MskuInventoryDetail
from models.msku_inventory_index import MskuInventoryIndex
from models.shipments_order import ShipmentsOrder
from models.sku_inventory_detail import SkuInventoryDetail
from models.sku_inventory_index import SkuInventoryIndex
from utils.common import get_today_time_int

app = Sanic.get_app(APP_NAME)


async def inbound(skus, campany_id):
    # 入库
    for sku, info in skus.items():
        inboundCount = info.get("inboundCount", None)
        if inboundCount == 0:
            continue
        inboundWarehouseId = info.get("inboundWarehouseId", None)
        skuBatchNumber = info.get("skuBatchNumber", None)
        if not skuBatchNumber:
            skuBatchNumber=int(time.time())
        skuInboundDate = get_today_time_int()
        fee = info.get("fee", None)
        operations = [UpdateOne({
            "campanyId": campany_id,
            "whId": inboundWarehouseId,
            "sku": sku,
            "skuBatchNumber": skuBatchNumber,
            "skuBatchOrder": index
        }, {"$set": {
            "campanyId": campany_id,
            "whId": inboundWarehouseId,
            "sku": sku,
            "skuBatchNumber": skuBatchNumber,
            "skuBatchOrder": index,
            "skuFee": (fee * 1.0 / inboundCount) / 100.0,
            "skuInboundDate": skuInboundDate,
            "tip": "",
            "skuStatus": 0,
            "shipmentsOrderId": None,
            "packingOrderId": None,
            "toEan": None,
            "toMskuBatchNumber": None,
            "toMskuBatchOrder": None,
            "skuHasSend":False,
        }}, upsert=True) for index in range(inboundCount)]
        # 执行批量操作
        if operations:
            collection_sku_inventory_detail: AsyncIOMotorCollection = app.ctx.mongo[SkuInventoryDetail.collection_name]
            await collection_sku_inventory_detail.bulk_write(operations, ordered=True)
        sku_index_data = await get_full_data_by_sku(sku=sku, campany_id=campany_id, wh_id=inboundWarehouseId)
        collection_sku_inventory_index: AsyncIOMotorCollection = app.ctx.mongo[SkuInventoryIndex.collection_name]

        if not sku_index_data:
            await collection_sku_inventory_index.update_one({
                "campanyId": campany_id,
                "whId": inboundWarehouseId,
                "sku": sku,
            }, {"$set": {
                "campanyId": campany_id,
                "whId": inboundWarehouseId,
                "sku": sku,
                "skuAvgFee": (fee * 1.0 / inboundCount) / 100.0,
                "skuTotalFee": fee / 100.0,
                "skuBuyTimes": 1,
                "skuLeft": inboundCount,
                "skuTotalBuy": inboundCount,
                "skuHasSend": 0,
                "skuInBox": 0,
                "skuInTrans": 0,
                "skuDealByUs": 0,
                "skuBeDestroied": 0,
                "deleted": False
            }}, upsert=True)
        else:
            skuTotalBuy = sku_index_data.get("skuTotalBuy", 0) + inboundCount
            skuTotalFee = sku_index_data.get("skuTotalFee", 0) + fee / 100.0
            skuBuyTimes = sku_index_data.get("skuBuyTimes", 0) + 1
            skuLeft = sku_index_data.get("skuLeft", 0) + inboundCount
            skuAvgFee = skuTotalFee * 1.0 / skuTotalBuy

            await collection_sku_inventory_index.update_one({
                "campanyId": campany_id,
                "whId": inboundWarehouseId,
                "sku": sku,
            }, {"$set": {
                "campanyId": campany_id,
                "whId": inboundWarehouseId,
                "sku": sku,
                "skuAvgFee": skuAvgFee,
                "skuTotalFee": skuTotalFee,
                "skuBuyTimes": skuBuyTimes,
                "skuLeft": skuLeft,
                "skuTotalBuy": skuTotalBuy,
            }}, upsert=True)


async def change_sku_inbound_info(campany_id, sku, inboundWarehouseId, oldInboundCount, oldFee, newInboundCount, newFee,
                                  skuBatchNumber):
    collection_sku_inventory_detail: AsyncIOMotorCollection = app.ctx.mongo[SkuInventoryDetail.collection_name]
    skuInboundDate = get_today_time_int()
    if newInboundCount < oldInboundCount:
        operations = [
            UpdateOne(
                {
                    "campanyId": campany_id,
                    "whId": inboundWarehouseId,
                    "sku": sku,
                    "skuBatchNumber": skuBatchNumber,
                    "skuBatchOrder": index
                },
                {"$set": {
                    "campanyId": campany_id,
                    "whId": inboundWarehouseId,
                    "sku": sku,
                    "skuBatchNumber": skuBatchNumber,
                    "skuBatchOrder": index,
                    "skuFee": (newFee * 1.0 / newInboundCount) / 100.0,
                }}, upsert=True) if index < newInboundCount else DeleteOne({
                "campanyId": campany_id,
                "whId": inboundWarehouseId,
                "sku": sku,
                "skuBatchNumber": skuBatchNumber,
                "skuBatchOrder": index
            }) for index in range(oldInboundCount)]
        # 执行批量操作
        if operations:
            await collection_sku_inventory_detail.bulk_write(operations, ordered=True)
    else:
        operations = [UpdateOne({
            "campanyId": campany_id,
            "whId": inboundWarehouseId,
            "sku": sku,
            "skuBatchNumber": skuBatchNumber,
            "skuBatchOrder": index
        }, {"$set": {
            "campanyId": campany_id,
            "whId": inboundWarehouseId,
            "sku": sku,
            "skuBatchNumber": skuBatchNumber,
            "skuBatchOrder": index,
            "skuFee": (newFee * 1.0 / newInboundCount) / 100.0,
        }}, upsert=True) if index < oldInboundCount else UpdateOne({
            "campanyId": campany_id,
            "whId": inboundWarehouseId,
            "sku": sku,
            "skuBatchNumber": skuBatchNumber,
            "skuBatchOrder": index
        }, {"$set": {
            "campanyId": campany_id,
            "whId": inboundWarehouseId,
            "sku": sku,
            "skuBatchNumber": skuBatchNumber,
            "skuBatchOrder": index,
            "skuInboundDate": skuInboundDate,
            "skuFee": (newFee * 1.0 / newInboundCount) / 100.0,
            "tip": "",
            "skuStatus": 0,
            "shipmentsOrderId": None,
            "packingOrderId": None,
            "toEan": None,
            "toMskuBatchNumber": None,
            "toMskuBatchOrder": None,
            "skuHasSend": False,
        }}, upsert=True) for index in range(newInboundCount)]
        # 执行批量操作
        if operations:
            await collection_sku_inventory_detail.bulk_write(operations, ordered=True)
    sku_index_data = await get_full_data_by_sku(sku=sku, campany_id=campany_id, wh_id=inboundWarehouseId)
    collection_sku_inventory_index: AsyncIOMotorCollection = app.ctx.mongo[SkuInventoryIndex.collection_name]
    if not sku_index_data:
        await collection_sku_inventory_index.update_one({
            "campanyId": campany_id,
            "whId": inboundWarehouseId,
            "sku": sku,
        }, {"$set": {
            "campanyId": campany_id,
            "whId": inboundWarehouseId,
            "sku": sku,
            "skuAvgFee": (newFee * 1.0 / newInboundCount) / 100.0,
            "skuTotalFee": newFee / 100.0,
            "skuBuyTimes": 1,
            "skuLeft": newInboundCount,
            "skuTotalBuy": newInboundCount,
            "skuHasSend": 0,
            "skuInBox": 0,
            "skuInTrans": 0,
            "skuDealByUs": 0,
            "skuBeDestroied": 0,
            "deleted": False
        }}, upsert=True)
    else:
        skuTotalBuy = sku_index_data.get("skuTotalBuy", 0) + newInboundCount - oldInboundCount
        skuTotalFee = sku_index_data.get("skuTotalFee", 0) + (newFee - oldFee) / 100.0
        skuLeft = sku_index_data.get("skuLeft", 0) + (newInboundCount - oldInboundCount)
        skuAvgFee = skuTotalFee * 1.0 / skuTotalBuy

        await collection_sku_inventory_index.update_one({
            "campanyId": campany_id,
            "whId": inboundWarehouseId,
            "sku": sku,
        }, {"$set": {
            "campanyId": campany_id,
            "whId": inboundWarehouseId,
            "sku": sku,
            "skuAvgFee": skuAvgFee,
            "skuTotalFee": skuTotalFee,
            "skuLeft": skuLeft,
            "skuTotalBuy": skuTotalBuy,
            "deleted": False
        }}, upsert=True)


async def change_sku_status_for_shipments_order(campany_id, packingOrderId, shipmentsOrderId, eanInfo, sendFromWhId,
                                                sendToWhId):
    """
    生成发货单时修改sku状态
    """
    collection_sku_inventory_detail: AsyncIOMotorCollection = app.ctx.mongo[SkuInventoryDetail.collection_name]
    collection_sku_inventory_index: AsyncIOMotorCollection = app.ctx.mongo[SkuInventoryIndex.collection_name]
    collection_msku_inventory_index: AsyncIOMotorCollection = app.ctx.mongo[MskuInventoryIndex.collection_name]
    await collection_sku_inventory_detail.update_many({"whId": sendFromWhId, "packingOrderId": packingOrderId}, {
        "$set": {"skuHasSend": True, "shipmentsOrderId": shipmentsOrderId, "skuStatus": 2}})
    sku_update = {}
    for item in eanInfo:
        is_ok, sku_data = await get_sku_data_by_ean(item["ean"], campany_id)
        if not is_ok:
            return False, "添加失败"
        for idx in range(1, item["count"] + 1):
            skusInfo = []
            mskuFee = 0
            for sku_info in sku_data:
                sku = sku_info["sku"]
                count_per_sku = sku_info["count"]
                sku_update[sku] = sku_update.get(sku, 0) + count_per_sku
                cursor = collection_sku_inventory_detail.find(
                    {"whId": sendFromWhId, "packingOrderId": packingOrderId, "shipmentsOrderId": shipmentsOrderId,
                     "sku": sku,"toMskuBatchOrder":None}).sort(["skuBatchNumber", "skuBatchOrder"]).limit(count_per_sku)
                update_operations = []
                async for doc in cursor:
                    # 构建更新操作
                    skusInfo.append({
                        "whId": sendFromWhId,
                        "sku": sku,
                        "skuBatchNumber": doc.get("skuBatchNumber", None),
                        "skuBatchOrder": doc.get("skuBatchOrder", None),
                        "skuFee": doc.get("skuFee", None),
                    })
                    mskuFee += doc.get("skuFee", 0)
                    update_operations.append(UpdateOne({"_id": doc["_id"]}, {"$set": {"toMskuBatchOrder": idx}}))
                if update_operations:
                    # 执行批量更新操作
                    result = await collection_sku_inventory_detail.bulk_write(update_operations)
            await change_ean_for_shipments_order(campany_id, item["ean"], mskuFee, idx, sendToWhId, shipmentsOrderId,
                                                 skusInfo)
        if await collection_msku_inventory_index.find_one({
            "campanyId": campany_id,
            "whId": sendToWhId,
            "ean": item["ean"]
        }):
            await collection_msku_inventory_index.update_one({
                "campanyId": campany_id,
                "whId": sendToWhId,
                "ean": item["ean"]
            }, {
                "$inc": {
                    "mskuSendTimes": 1,
                    "mskuInTrans": item["count"],
                    "mskuTotalSent": item["count"],
                }
            },upsert=True)
        else:
            await collection_msku_inventory_index.insert_one({
                "campanyId": campany_id,
                "whId": sendToWhId,
                "ean": item["ean"],
                "mskuAvgBuyAndHeadFee": None,
                "mskuAvgFee": None,
                "mskuAvgHeadFee": None,
                "mskuFinallInboundDate": None,
                "mskuFirstInboundDate": None,
                "mskuHasDestroyed": 0,
                "mskuHasLosed": 0,
                "mskuHasPurchased": 0,
                "mskuSendTimes": 1,
                "mskuTotalBuyAndHeadFee": None,
                "mskuTotalFee": None,
                "mskuTotalHeadFee": None,
                "mskuTotalSent": item["count"],
                "mskuLeft": 0,
                "mskuInTrans": item["count"]
            })
    for sku_, count_ in sku_update.items():
        await collection_sku_inventory_index.update_one({
            "campanyId": campany_id,
            "whId": sendFromWhId,
            "sku": sku_
        }, {
            "$inc": {
                "skuInBox": -count_,
                "skuHasSend": count_,
                "skuInTrans": count_
            }
        })


async def change_sku_status_for_shipments_order_inbound(campany_id, shipmentsOrderId):
    """
    生成发货单时修改sku状态
    """
    today = get_today_time_int()
    collection_sku_inventory_detail: AsyncIOMotorCollection = app.ctx.mongo[SkuInventoryDetail.collection_name]
    collection_sku_inventory_index: AsyncIOMotorCollection = app.ctx.mongo[SkuInventoryIndex.collection_name]
    collection_msku_inventory_index: AsyncIOMotorCollection = app.ctx.mongo[MskuInventoryIndex.collection_name]
    collection_msku_inventory_detail: AsyncIOMotorCollection = app.ctx.mongo[MskuInventoryDetail.collection_name]

    collection_shipments_order: AsyncIOMotorCollection = app.ctx.mongo[ShipmentsOrder.collection_name]
    #
    shipmentsOrderData = await collection_shipments_order.find_one(
        {"campanyId": campany_id, "shipmentsOrderId": shipmentsOrderId})
    eanInfo = shipmentsOrderData.get("eanInfo", None)
    sendFromWhId = shipmentsOrderData.get("sendFromWhId", None)
    sendToWhId = shipmentsOrderData.get("sendToWhId", None)
    total_price = shipmentsOrderData.get("domesticLogisticsInfo", {}).get("price", 0) + shipmentsOrderData.get(
        "internationalLogisticsInfo", {}).get("price", 0)
    ean_weighing = await get_weighing_info_by_eans([i["ean"] for i in eanInfo], campany_id)
    total_weighing = sum([ean_weighing.get(i["ean"], None) * i["count"] for i in eanInfo])
    msku_head_fee = {k: total_price * v / total_weighing for k, v in ean_weighing.items()}
    #
    await collection_sku_inventory_detail.update_many(
        {"whId": sendFromWhId, "shipmentsOrderId": shipmentsOrderId, "skuStatus": 2}, {
            "$set": {"skuStatus": 3,"toMskuBatchNumber":today}})
    sku_update = {}
    for item in eanInfo:
        is_ok, sku_data = await get_sku_data_by_ean(item["ean"], campany_id)
        if not is_ok:
            return False, "添加失败"
        for idx in range(1, item["count"] + 1):
            for sku_info in sku_data:
                sku = sku_info["sku"]
                count_per_sku = sku_info["count"]
                sku_update[sku] = sku_update.get(sku, 0) + count_per_sku

        #
        await change_ean_for_shipments_order_inbound(campany_id, item["ean"], today, today,
                                                     msku_head_fee.get(item["ean"], 0),
                                                     sendToWhId, shipmentsOrderId)
        cursor = collection_msku_inventory_detail.find({"campanyId": campany_id, "ean": item["ean"],"whId":sendToWhId})

        day_set = set()
        shipmentsOrderId_set = set()
        mskuTotalFee = 0
        mskuTotalHeadFee = 0
        mskuTotalBuyAndHeadFee = 0
        mskuTotalSent = 0
        mskuLeft = 0
        mskuInTrans = 0
        mskuHasDestroyed = 0
        mskuHasLosed = 0
        mskuHasPurchased = 0
        async for doc in cursor:
            if doc.get("mskuBatchNumber",None):
                day_set.add(doc.get("mskuBatchNumber",None))
            shipmentsOrderId_set.add(doc.get("shipmentsOrderId",None))
            mskuTotalFee += doc.get("mskuFee",0)
            mskuTotalHeadFee += (doc.get("mskuHeadFee",0) if doc.get("mskuHeadFee",0) else 0)
            mskuTotalBuyAndHeadFee += (doc.get("mskuBuyAndHeadFee",0) if doc.get("mskuBuyAndHeadFee",0) else 0)
            mskuTotalSent+=1
            # 0:在库 1:售出 2:在途 3:入仓丢失 4:销毁
            if doc.get("status",0)==0:
                mskuLeft+=1
            elif doc.get("status",0)==2:
                mskuInTrans+=1
            elif doc.get("status",0)==4:
                mskuHasDestroyed+=1
            elif doc.get("status",0)==3:
                mskuHasLosed+=1
            elif doc.get("status",0)==1:
                mskuHasPurchased+=1
        index_info = {
            # "whId": sendToWhId,
            # "ean": item["ean"],
            # "campanyId": campany_id,
            "mskuAvgBuyAndHeadFee": mskuTotalBuyAndHeadFee/mskuTotalSent,
            "mskuAvgFee": mskuTotalFee/mskuTotalSent,
            "mskuAvgHeadFee": mskuTotalHeadFee/mskuTotalSent,
            "mskuFinallInboundDate": max(list(day_set)),
            "mskuFirstInboundDate":  min(list(day_set)),
            "mskuHasDestroyed": mskuHasDestroyed,
            "mskuHasLosed": mskuHasLosed,
            "mskuHasPurchased": mskuHasPurchased,
            "mskuSendTimes": len(shipmentsOrderId_set),
            "mskuTotalBuyAndHeadFee": mskuTotalBuyAndHeadFee,
            "mskuTotalFee": mskuTotalFee,
            "mskuTotalHeadFee": mskuTotalHeadFee,
            "mskuTotalSent": mskuTotalSent,
            "mskuLeft": mskuLeft,
            "mskuInTrans": mskuInTrans
        }
        await collection_msku_inventory_index.update_one({"campanyId": campany_id, "ean": item["ean"],"whId":sendToWhId},{"$set":index_info},upsert=True)

    for sku_, count_ in sku_update.items():
        await collection_sku_inventory_index.update_one({
            "campanyId": campany_id,
            "whId": sendFromWhId,
            "sku": sku_
        }, {
            "$inc": {
                "skuInTrans": -count_
            }
        })
    return True,"ok"
