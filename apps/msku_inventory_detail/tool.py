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

from motor.motor_asyncio import AsyncIOMotorCollection
from sanic import Sanic

from apps.listing.tool import get_stock_info_by_eans
from apps.overseas_warehouse.tool import get_shop_whid
from config.constant import APP_NAME
from models.msku_inventory_detail import MskuInventoryDetail
from models.msku_inventory_index import MskuInventoryIndex
from utils.common import get_store_days, int_day_dec_days, generate_year_weeks, get_day_range, get_month_range, \
    get_year_range

app = Sanic.get_app(APP_NAME)


async def change_ean_for_shipments_order(campanyId, ean, mskuFee, mskuBatchOrder, sendToWhId, shipmentsOrderId,
                                         skusInfo):
    collection_msku_inventory_detail: AsyncIOMotorCollection = app.ctx.mongo[MskuInventoryDetail.collection_name]
    await collection_msku_inventory_detail.update_one(
        {"campanyId": campanyId, "whId": sendToWhId, "ean": ean, "mskuBatchOrder": mskuBatchOrder,
         "shipmentsOrderId": shipmentsOrderId},
        {"$set": {"mskuBatchNumber": None, "mskuFee": mskuFee, "mskuHeadFee": None, "mskuBuyAndHeadFee": None,
                  "mskuInboundDate": None, "skusInfo": skusInfo, "status": 2, "buyCountry": None, "orderId": None,
                  "statusVersion": None, "tip": "", "deleted": False}}, upsert=True)


async def change_ean_for_shipments_order_inbound(campanyId, ean, mskuBatchNumber, mskuInboundDate, mskuHeadFee,
                                                 sendToWhId, shipmentsOrderId):
    collection_msku_inventory_detail: AsyncIOMotorCollection = app.ctx.mongo[MskuInventoryDetail.collection_name]
    cursor = collection_msku_inventory_detail.find(
        {"campanyId": campanyId, "whId": sendToWhId, "ean": ean, "shipmentsOrderId": shipmentsOrderId})
    async for doc in cursor:
        mskuFee = doc.get("mskuFee", 0)
        mskuBatchOrder = doc.get("mskuBatchOrder", None)
        mskuBuyAndHeadFee = mskuFee + mskuHeadFee
        await collection_msku_inventory_detail.update_one(
            {"campanyId": campanyId, "whId": sendToWhId, "ean": ean, "mskuBatchOrder": mskuBatchOrder,
             "shipmentsOrderId": shipmentsOrderId},
            {"$set": {"mskuBatchNumber": mskuBatchNumber, "mskuHeadFee": mskuHeadFee,
                      "mskuBuyAndHeadFee": mskuBuyAndHeadFee,
                      "mskuInboundDate": mskuInboundDate, "status": 0}})


# 统计库存情况
async def count_status_by_batch(company_id: str, eans: list):
    collection_msku_inventory_detail: AsyncIOMotorCollection = app.ctx.mongo[MskuInventoryDetail.collection_name]
    # 聚合管道
    pipeline = [
        {
            "$match": {
                "campanyId": company_id,
                "status": {"$ne": 2},
                "ean": {"$in": eans}
            }
        },
        {
            "$group": {
                "_id": {
                    "ean": "$ean",
                    "mskuBatchNumber": "$mskuBatchNumber",
                    "status": "$status"
                },
                "count": {"$sum": 1}
            }
        },
        {"$project": {"_id": 0, "ean": "$_id.ean", "mskuBatchNumber": "$_id.mskuBatchNumber", "status": "$_id.status",
                      "count": "$count"}},
        {"$sort": {"mskuBatchNumber": 1}}
    ]

    # 执行聚合查询
    results = {}
    async for doc in collection_msku_inventory_detail.aggregate(pipeline):
        # 转换为更友好的格式
        if doc["ean"] not in results:
            results[doc["ean"]] = {}
        if doc["mskuBatchNumber"] not in results[doc["ean"]]:
            results[doc["ean"]][doc["mskuBatchNumber"]] = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
        results[doc["ean"]][doc["mskuBatchNumber"]][doc["status"]] = doc["count"]
    for ean, v in results.items():
        results[ean] = [{"batch": i[0], "statusCount": i[1], "storeDays": get_store_days(i[0])} for i in
                        sorted(v.items(), key=lambda x: x[0])]
    return results


async def count_sold_by_batch(company_id: str, eans: list):
    collection_msku_inventory_detail: AsyncIOMotorCollection = app.ctx.mongo[MskuInventoryDetail.collection_name]
    # 聚合管道
    pipeline = [
        {
            "$match": {
                "campanyId": company_id,
                "status": 1,
                "ean": {"$in": eans}
            }
        },
        {
            "$group": {
                "_id": "$ean",
                "week": {
                    "$sum": {
                        "$cond": [{"$gte": ["$orderCreateDate", int_day_dec_days(7)]}, 1, 0]
                    }
                },
                "month": {
                    "$sum": {
                        "$cond": [{"$gte": ["$orderCreateDate", int_day_dec_days(30)]}, 1, 0]
                    }
                },
                "season": {
                    "$sum": {
                        "$cond": [{"$gte": ["$orderCreateDate", int_day_dec_days(90)]}, 1, 0]
                    }
                },
                "year": {
                    "$sum": {
                        "$cond": [{"$gte": ["$orderCreateDate", int_day_dec_days(365)]}, 1, 0]
                    }
                }
            }
        },
        {"$project": {"_id": 1, "week": 1, "month": 1, "season": 1, "year": 1}},
    ]

    # 执行聚合查询
    results = {}
    async for doc in collection_msku_inventory_detail.aggregate(pipeline):
        # 转换为更友好的格式
        # results[doc["ean"]] = doc
        results[doc["_id"]] = {'week': doc["week"], 'month': doc["month"], 'season': doc["season"], 'year': doc["year"]}
    return results


async def get_ean_sold_per_day(company_id: str, ean: str | None):
    collection_msku_inventory_detail: AsyncIOMotorCollection = app.ctx.mongo[MskuInventoryDetail.collection_name]
    # 聚合管道
    pipeline = [
        {
            "$match": {
                "campanyId": company_id,
                "status": 1,
                "ean": ean
            } if ean else {
                "campanyId": company_id,
                "status": 1}
        },
        {
            "$group": {
                "_id": {
                    '$dateToString': {
                        'format': '%Y-%m-%d',
                        'date': '$orderCreateDateTime'
                    }
                },
                'totalOrderCount': {'$sum': 1},
            }
        },
        {
            '$project': {
                # 28zhou
                'totalOrderCount': 1,
            }
        },
        {
            '$sort': {'_id': 1}
        }
    ]

    # 执行聚合查询
    results = {}
    start_date = None
    async for doc in collection_msku_inventory_detail.aggregate(pipeline):
        # 转换为更友好的格式
        if not start_date:
            start_date = doc["_id"]
        results[doc["_id"]] = doc["totalOrderCount"]
    days = get_day_range(start_date)
    sold_count = [results.get(i, 0) for i in days]
    return days, sold_count


async def get_ean_sold_per_week(company_id: str, ean: str | None):
    collection_msku_inventory_detail: AsyncIOMotorCollection = app.ctx.mongo[MskuInventoryDetail.collection_name]
    # 聚合管道
    pipeline = [
        {
            "$match": {
                "campanyId": company_id,
                "status": 1,
                "ean": ean
            } if ean else {
                "campanyId": company_id,
                "status": 1
            }
        },
        {
            '$group': {
                '_id': {
                    'year': {'$year': '$orderCreateDateTime'},
                    'week': {'$week': '$orderCreateDateTime'}
                },
                'totalOrderCount': {'$sum': 1},
                'start_date': {'$min': '$orderCreateDateTime'},
                'end_date': {'$max': '$orderCreateDateTime'}
            }
        },
        {
            '$project': {
                # 28zhou
                'totalOrderCount': 1,
            }
        },
        {
            '$sort': {'_id': 1}
        }
    ]

    # 执行聚合查询
    results = []
    async for doc in collection_msku_inventory_detail.aggregate(pipeline):
        # 转换为更友好的格式
        results.append(doc)
    if results:
        year_weeks, year_weeks_date_range = generate_year_weeks(results[0]["_id"]["year"], results[0]["_id"]["week"])
    else:
        year_weeks, year_weeks_date_range = generate_year_weeks(None, None)
    results = {f'{i["_id"]["year"]}-{i["_id"]["week"]}': i["totalOrderCount"] for i in results}
    sold_count = [results.get(f'{i[0]}-{i[1]}', 0) for i in year_weeks]
    return year_weeks_date_range, sold_count


async def get_ean_sold_per_month(company_id: str, ean: str | None):
    collection_msku_inventory_detail: AsyncIOMotorCollection = app.ctx.mongo[MskuInventoryDetail.collection_name]
    # 聚合管道
    pipeline = [
        {
            "$match": {
                "campanyId": company_id,
                "status": 1,
                "ean": ean
            } if ean else {
                "campanyId": company_id,
                "status": 1}
        },
        {
            "$group": {
                "_id": {
                    '$dateToString': {
                        'format': '%Y-%m',
                        'date': '$orderCreateDateTime'
                    }
                },
                'totalOrderCount': {'$sum': 1},
            }
        },
        {
            '$project': {
                # 28zhou
                'totalOrderCount': 1,
            }
        },
        {
            '$sort': {'_id': 1}
        }
    ]

    # 执行聚合查询
    results = {}
    start_date = None
    async for doc in collection_msku_inventory_detail.aggregate(pipeline):
        # 转换为更友好的格式
        if not start_date:
            start_date = doc["_id"]
        results[doc["_id"]] = doc["totalOrderCount"]
    months = get_month_range(start_date)
    sold_count = [results.get(i, 0) for i in months]
    return months, sold_count


async def get_ean_sold_per_year(company_id: str, ean: str | None):
    collection_msku_inventory_detail: AsyncIOMotorCollection = app.ctx.mongo[MskuInventoryDetail.collection_name]
    # 聚合管道
    pipeline = [
        {
            "$match": {
                "campanyId": company_id,
                "status": 1,
                "ean": ean
            } if ean else {
                "campanyId": company_id,
                "status": 1}
        },
        {
            "$group": {
                "_id": {
                    '$dateToString': {
                        'format': '%Y',
                        'date': '$orderCreateDateTime'
                    }
                },
                'totalOrderCount': {'$sum': 1},
            }
        },
        {
            '$project': {
                # 28zhou
                'totalOrderCount': 1,
            }
        },
        {
            '$sort': {'_id': 1}
        }
    ]

    # 执行聚合查询
    results = {}
    start_date = None
    async for doc in collection_msku_inventory_detail.aggregate(pipeline):
        # 转换为更友好的格式
        if not start_date:
            start_date = doc["_id"]
        results[doc["_id"]] = doc["totalOrderCount"]
    years = get_year_range(start_date)
    sold_count = [results.get(i, 0) for i in years]
    return years, sold_count


async def get_today_in_trans(company_id, shop):
    whId = await get_shop_whid(company_id, shop)
    collection_msku_inventory_detail: AsyncIOMotorCollection = app.ctx.mongo[MskuInventoryDetail.collection_name]
    collection_msku_inventory_index: AsyncIOMotorCollection = app.ctx.mongo[MskuInventoryIndex.collection_name]
    # 聚合管道
    pipeline = [
        {
            "$match": {
                "campanyId": company_id,
                "status": 2,
                "whId": whId
            }
        },
        {
            "$group": {
                "_id": {
                    'ean': "$ean",
                    "shipmentsOrderId":"$shipmentsOrderId"
                },
                'inTransCount': {'$sum': 1},
            }
        },
        {
            '$project': {
                # 28zhou
                "_id":1,
                'inTransCount': 1,
            }
        },
        {
            '$sort': {'_id': 1}
        }
    ]
    results = []
    eans = set()
    async for doc in collection_msku_inventory_detail.aggregate(pipeline):
        results.append({**doc["_id"],"inTransCount":doc["inTransCount"]})
        eans.add(doc["_id"]["ean"])
    if not results:
        return []
    eans = list(eans)
    msku_left = await collection_msku_inventory_index.find({"campanyId":company_id,"ean":{"$in":eans},"whId":whId},{"ean":1,"mskuLeft":1}).to_list()
    msku_left = {i["ean"]: i["mskuLeft"] for i in msku_left}
    stock_images_data = await get_stock_info_by_eans(eans,company_id)
    for i in results:
        i["mskuLeft"] = msku_left.get(i["ean"])
        i["stock"] = stock_images_data.get(i["ean"],{}).get("stock",None)
        i["images"] = stock_images_data.get(i["ean"],{}).get("images",[])
    return results




