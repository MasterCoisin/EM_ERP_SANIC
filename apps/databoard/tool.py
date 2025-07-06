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
@Date        ：2025-06-04 17:08 
-------------------------------------
'''
from motor.motor_asyncio import AsyncIOMotorCollection
from sanic import Sanic

from apps.overseas_warehouse.tool import get_shop_whid
from config.constant import APP_NAME
from models.em_order import EmOrder
from models.msku_inventory_detail import MskuInventoryDetail
from utils.common import get_store_days, int_day_dec_days, generate_year_weeks, get_day_range, get_month_range, \
    get_year_range

app = Sanic.get_app(APP_NAME)


async def get_order_trency(campany_id, shop, order_status):
    trency_per_day = await get_order_trency_per_day(campany_id, shop, order_status)
    trency_per_week = await get_order_trency_per_week(campany_id, shop, order_status)
    trency_per_month = await get_order_trency_per_month(campany_id, shop, order_status)
    trency_per_year = await get_order_trency_per_year(campany_id, shop, order_status)
    stock_value = await get_stock_value(campany_id, shop)
    chartData = {
        "total_order_count": {
            "today": trency_per_day["total"]["soldCount"][-1],
            "yesterday": trency_per_day["total"]["soldCount"][-2] if len(
                trency_per_day["total"]["soldCount"]) > 1 else 0,
            "this_week": trency_per_week["total"]["soldCount"][-1],
            "last_week": trency_per_week["total"]["soldCount"][-2] if len(
                trency_per_week["total"]["soldCount"]) > 1 else 0,
            "this_month": trency_per_month["total"]["soldCount"][-1],
            "last_month": trency_per_month["total"]["soldCount"][-2] if len(
                trency_per_month["total"]["soldCount"]) > 1 else 0,
            "this_year": trency_per_year["total"]["soldCount"][-1],
            "last_year": trency_per_year["total"]["soldCount"][-2] if len(
                trency_per_year["total"]["soldCount"]) > 1 else 0,
            "total": sum(trency_per_day["total"]["soldCount"])
        },
        "total_order_count_ro": {
            "today": trency_per_day["ro"]["soldCount"][-1],
            "yesterday": trency_per_day["ro"]["soldCount"][-2] if len(trency_per_day["ro"]["soldCount"]) > 1 else 0,
            "this_week": trency_per_week["ro"]["soldCount"][-1],
            "last_week": trency_per_week["ro"]["soldCount"][-2] if len(
                trency_per_week["ro"]["soldCount"]) > 1 else 0,
            "this_month": trency_per_month["ro"]["soldCount"][-1],
            "last_month": trency_per_month["ro"]["soldCount"][-2] if len(
                trency_per_month["ro"]["soldCount"]) > 1 else 0,
            "this_year": trency_per_year["ro"]["soldCount"][-1],
            "last_year": trency_per_year["ro"]["soldCount"][-2] if len(
                trency_per_year["ro"]["soldCount"]) > 1 else 0,
            "total": sum(trency_per_day["ro"]["soldCount"])
        },
        "total_order_count_bg": {
            "today": trency_per_day["bg"]["soldCount"][-1],
            "yesterday": trency_per_day["bg"]["soldCount"][-2] if len(trency_per_day["bg"]["soldCount"]) > 1 else 0,
            "this_week": trency_per_week["bg"]["soldCount"][-1],
            "last_week": trency_per_week["bg"]["soldCount"][-2] if len(
                trency_per_week["bg"]["soldCount"]) > 1 else 0,
            "this_month": trency_per_month["bg"]["soldCount"][-1],
            "last_month": trency_per_month["bg"]["soldCount"][-2] if len(
                trency_per_month["bg"]["soldCount"]) > 1 else 0,
            "this_year": trency_per_year["bg"]["soldCount"][-1],
            "last_year": trency_per_year["bg"]["soldCount"][-2] if len(
                trency_per_year["bg"]["soldCount"]) > 1 else 0,
            "total": sum(trency_per_day["bg"]["soldCount"])
        },
        "total_order_count_hu": {
            "today": trency_per_day["hu"]["soldCount"][-1],
            "yesterday": trency_per_day["hu"]["soldCount"][-2] if len(trency_per_day["hu"]["soldCount"]) > 1 else 0,
            "this_week": trency_per_week["hu"]["soldCount"][-1],
            "last_week": trency_per_week["hu"]["soldCount"][-2] if len(trency_per_week["hu"]["soldCount"]) > 1 else 0,
            "this_month": trency_per_month["hu"]["soldCount"][-1],
            "last_month": trency_per_month["hu"]["soldCount"][-2] if len(trency_per_month["hu"]["soldCount"]) > 1 else 0,
            "this_year": trency_per_year["hu"]["soldCount"][-1],
            "last_year": trency_per_year["hu"]["soldCount"][-2] if len(
                trency_per_year["hu"]["soldCount"]) > 1 else 0,
            "total": sum(trency_per_day["hu"]["soldCount"])
        },
        "total_amount": {
            "today": trency_per_day["total"]["soldAmount"][-1],
            "yesterday": trency_per_day["total"]["soldAmount"][-2] if len(
                trency_per_day["total"]["soldAmount"]) > 1 else 0,
            "this_week": trency_per_week["total"]["soldAmount"][-1],
            "last_week": trency_per_week["total"]["soldAmount"][-2] if len(
                trency_per_week["total"]["soldAmount"]) > 1 else 0,
            "this_month": trency_per_month["total"]["soldAmount"][-1],
            "last_month": trency_per_month["total"]["soldAmount"][-2] if len(
                trency_per_month["total"]["soldAmount"]) > 1 else 0,
            "total": round(sum(trency_per_day["total"]["soldAmount"]), 2)
        },
        "in_stock_count": {
            "today": stock_value[0]["count"],
            "yesterday": 99999,
        },
        "in_trans_count": {
            "today": stock_value[2]["count"],
            "yesterday": 99999,
        },
        "has_sold_count": {
            "today": stock_value[1]["count"],
            "yesterday": 3,
        },
         # "0:在库 1:售出 2:在途 3:入仓丢失 4:销毁"
        "distribution_of_goods_value": {
            "goods_value_of_sold": round(stock_value[1]["value"],2),  # 已售货值
            "goods_value_of_in_stock": round(stock_value[0]["value"],2),  # 在售货值
            "goods_value_of_in_trans": round(stock_value[2]["value"],2),  # 在途货值
            "goods_value_of_destroy": round(stock_value[4]["value"],2),  # 销毁货值
            "goods_value_of_loss": round(stock_value[3]["value"],2),  # 丢失货值
        },
        "order_count_trend": {
            "day": trency_per_day,
            "week": trency_per_week,
            "month": trency_per_month,
            "year": trency_per_year
        }
    }
    return chartData


async def get_order_trency_per_day(campany_id, shop, order_status):
    collection_em_order: AsyncIOMotorCollection = app.ctx.mongo[EmOrder.collection_name]
    # 聚合管道
    pipeline = [
        {
            "$match": {
                "campanyId": campany_id,
                "status": {"$in": [int(i) for i in order_status]},
                "shop": shop
            }
        },
        {
            "$group": {
                "_id": {
                    "date": {
                        '$dateToString': {
                            'format': '%Y-%m-%d',
                            'date': '$date'
                        }
                    },
                    'country': '$country'
                },
                'totalOrderCount': {'$sum': 1},
                'totalPriceRmb': {'$sum': '$totalPriceRmb'},
            }
        },
        {
            '$project': {
                # 28zhou
                '_id': 1,
                'totalOrderCount': 1,
                'totalPriceRmb': 1
            }
        },
        {
            '$sort': {'_id': 1}
        }
    ]
    # 执行聚合查询
    resultsTotalOrderCount = {"ro": {}, "bg": {}, "hu": {}, "total": {}}
    resultsTotalPriceRmb = {"ro": {}, "bg": {}, "hu": {}, "total": {}}
    start_date = {"ro": None, "bg": None, "hu": None, "total": None}
    async for doc in collection_em_order.aggregate(pipeline):
        # 转换为更友好的格式
        if start_date[doc["_id"]["country"]] is None or (
                int(start_date[doc["_id"]["country"]].replace("-", "")) > int(doc["_id"]["date"].replace("-", ""))):
            start_date[doc["_id"]["country"]] = doc["_id"]["date"]
        if start_date["total"] is None or (
                int(start_date["total"].replace("-", "")) > int(doc["_id"]["date"].replace("-", ""))):
            start_date["total"] = doc["_id"]["date"]

        resultsTotalOrderCount[doc["_id"]["country"]][doc["_id"]["date"]] = doc["totalOrderCount"]
        resultsTotalPriceRmb[doc["_id"]["country"]][doc["_id"]["date"]] = doc["totalPriceRmb"]

        resultsTotalOrderCount["total"][doc["_id"]["date"]] = doc["totalOrderCount"] + resultsTotalOrderCount[
            "total"].get(doc["_id"]["date"], 0)
        resultsTotalPriceRmb["total"][doc["_id"]["date"]] = doc["totalPriceRmb"] + resultsTotalPriceRmb["total"].get(
            doc["_id"]["date"], 0)

    days_ro = get_day_range(start_date["ro"])
    days_bg = get_day_range(start_date["bg"])
    days_hu = get_day_range(start_date["hu"])
    days_total = get_day_range(start_date["total"])
    result = {
        "total": {
            "yDate": days_total,
            "soldCount": [resultsTotalOrderCount['total'].get(i, 0) for i in days_total],
            "soldAmount": [round(resultsTotalPriceRmb['total'].get(i, 0), 0) for i in days_total],
        },
        "ro": {
            "yDate": days_ro,
            "soldCount": [resultsTotalOrderCount['ro'].get(i, 0) for i in days_ro],
            "soldAmount": [round(resultsTotalPriceRmb['ro'].get(i, 0), 0) for i in days_ro],
        },
        "bg": {
            "yDate": days_bg,
            "soldCount": [resultsTotalOrderCount['bg'].get(i, 0) for i in days_bg],
            "soldAmount": [round(resultsTotalPriceRmb['bg'].get(i, 0), 0) for i in days_bg],
        },
        "hu": {
            "yDate": days_hu,
            "soldCount": [resultsTotalOrderCount['hu'].get(i, 0) for i in days_hu],
            "soldAmount": [round(resultsTotalPriceRmb['hu'].get(i, 0), 0) for i in days_hu],
        },
    }
    return result


async def get_order_trency_per_week(campany_id, shop, order_status):
    collection_em_order: AsyncIOMotorCollection = app.ctx.mongo[EmOrder.collection_name]
    # 聚合管道
    pipeline = [
        {
            "$match": {
                "campanyId": campany_id,
                "status": {"$in": [int(i) for i in order_status]},
                "shop": shop
            }
        },
        {
            "$group": {
                "_id": {
                    'year': {'$year': '$date'},
                    'week': {'$week': '$date'},
                    'country': '$country'
                },
                'totalOrderCount': {'$sum': 1},
                'totalPriceRmb': {'$sum': '$totalPriceRmb'},
            }
        },
        {
            '$project': {
                # 28zhou
                '_id': 1,
                'totalOrderCount': 1,
                'totalPriceRmb': 1
            }
        },
        {
            '$sort': {'_id': 1}
        }
    ]
    # 执行聚合查询
    resultsTotalOrderCount = {"ro": {}, "bg": {}, "hu": {}, "total": {}}
    resultsTotalPriceRmb = {"ro": {}, "bg": {}, "hu": {}, "total": {}}
    start_date = {"ro": None, "bg": None, "hu": None, "total": None}
    async for doc in collection_em_order.aggregate(pipeline):
        # 转换为更友好的格式
        if start_date[doc["_id"]["country"]] is None or (
                start_date[doc["_id"]["country"]]["year"] >= doc["_id"]["year"] and start_date[doc["_id"]["country"]][
            "week"] > doc["_id"]["week"]):
            start_date[doc["_id"]["country"]] = {"year": doc["_id"]["year"], "week": doc["_id"]["week"]}
        if start_date["total"] is None or (
                start_date["total"]["year"] >= doc["_id"]["year"] and start_date["total"]["week"] > doc["_id"]["week"]):
            start_date["total"] = {"year": doc["_id"]["year"], "week": doc["_id"]["week"]}

        resultsTotalOrderCount[doc["_id"]["country"]][f'{doc["_id"]["year"]}-{doc["_id"]["week"]}'] = doc[
            "totalOrderCount"]
        resultsTotalPriceRmb[doc["_id"]["country"]][f'{doc["_id"]["year"]}-{doc["_id"]["week"]}'] = doc["totalPriceRmb"]

        resultsTotalOrderCount["total"][f'{doc["_id"]["year"]}-{doc["_id"]["week"]}'] = doc["totalOrderCount"] + \
                                                                                        resultsTotalOrderCount[
                                                                                            "total"].get(
                                                                                            f'{doc["_id"]["year"]}-{doc["_id"]["week"]}',
                                                                                            0)
        resultsTotalPriceRmb["total"][f'{doc["_id"]["year"]}-{doc["_id"]["week"]}'] = doc["totalPriceRmb"] + \
                                                                                      resultsTotalPriceRmb["total"].get(
                                                                                          f'{doc["_id"]["year"]}-{doc["_id"]["week"]}',
                                                                                          0)
    year_weeks_ro, year_weeks_date_range_ro = generate_year_weeks(
        start_date["ro"]["year"] if start_date["ro"] else None, start_date["ro"]["week"] if start_date["ro"] else None)
    year_weeks_bg, year_weeks_date_range_bg = generate_year_weeks(
        start_date["bg"]["year"] if start_date["bg"] else None, start_date["bg"]["week"] if start_date["bg"] else None)
    year_weeks_hu, year_weeks_date_range_hu = generate_year_weeks(
        start_date["hu"]["year"] if start_date["hu"] else None, start_date["hu"]["week"] if start_date["hu"] else None)
    year_weeks_total, year_weeks_date_range_total = generate_year_weeks(
        start_date["total"]["year"] if start_date["total"] else None,
        start_date["total"]["week"] if start_date["total"] else None)

    result = {
        "total": {
            "yDate": [f"{i[0]} ~ {i[1]}" for i in year_weeks_date_range_total],
            "soldCount": [resultsTotalOrderCount['total'].get(f'{i[0]}-{i[1]}', 0) for i in year_weeks_total],
            "soldAmount": [round(resultsTotalPriceRmb['total'].get(f'{i[0]}-{i[1]}', 0), 0) for i in
                           year_weeks_total],
        },
        "ro": {
            "yDate": [f"{i[0]} ~ {i[1]}" for i in year_weeks_date_range_ro],
            "soldCount": [resultsTotalOrderCount['ro'].get(f'{i[0]}-{i[1]}', 0) for i in year_weeks_ro],
            "soldAmount": [round(resultsTotalPriceRmb['ro'].get(f'{i[0]}-{i[1]}', 0), 0) for i in
                           year_weeks_ro],
        },
        "bg": {
            "yDate": [f"{i[0]} ~ {i[1]}" for i in year_weeks_date_range_bg],
            "soldCount": [resultsTotalOrderCount['bg'].get(f'{i[0]}-{i[1]}', 0) for i in year_weeks_bg],
            "soldAmount": [round(resultsTotalPriceRmb['bg'].get(f'{i[0]}-{i[1]}', 0), 0) for i in
                           year_weeks_bg],
        },
        "hu": {
            "yDate": [f"{i[0]} ~ {i[1]}" for i in year_weeks_date_range_hu],
            "soldCount": [resultsTotalOrderCount['hu'].get(f'{i[0]}-{i[1]}', 0) for i in year_weeks_hu],
            "soldAmount": [round(resultsTotalPriceRmb['hu'].get(f'{i[0]}-{i[1]}', 0), 0) for i in
                           year_weeks_hu],
        },
    }
    return result


async def get_order_trency_per_month(campany_id, shop, order_status):
    collection_em_order: AsyncIOMotorCollection = app.ctx.mongo[EmOrder.collection_name]
    # 聚合管道
    pipeline = [
        {
            "$match": {
                "campanyId": campany_id,
                "status": {"$in": [int(i) for i in order_status]},
                "shop": shop
            }
        },
        {
            "$group": {
                "_id": {
                    "date": {
                        '$dateToString': {
                            'format': '%Y-%m',
                            'date': '$date'
                        }
                    },
                    'country': '$country'
                },
                'totalOrderCount': {'$sum': 1},
                'totalPriceRmb': {'$sum': '$totalPriceRmb'},
            }
        },
        {
            '$project': {
                # 28zhou
                '_id': 1,
                'totalOrderCount': 1,
                'totalPriceRmb': 1
            }
        },
        {
            '$sort': {'_id': 1}
        }
    ]
    # 执行聚合查询
    resultsTotalOrderCount = {"ro": {}, "bg": {}, "hu": {}, "total": {}}
    resultsTotalPriceRmb = {"ro": {}, "bg": {}, "hu": {}, "total": {}}
    start_date = {"ro": None, "bg": None, "hu": None, "total": None}
    async for doc in collection_em_order.aggregate(pipeline):
        # 转换为更友好的格式
        if start_date[doc["_id"]["country"]] is None or (
                int(start_date[doc["_id"]["country"]].replace("-", "")) > int(doc["_id"]["date"].replace("-", ""))):
            start_date[doc["_id"]["country"]] = doc["_id"]["date"]
        if start_date["total"] is None or (
                int(start_date["total"].replace("-", "")) > int(doc["_id"]["date"].replace("-", ""))):
            start_date["total"] = doc["_id"]["date"]

        resultsTotalOrderCount[doc["_id"]["country"]][doc["_id"]["date"]] = doc["totalOrderCount"]
        resultsTotalPriceRmb[doc["_id"]["country"]][doc["_id"]["date"]] = doc["totalPriceRmb"]

        resultsTotalOrderCount["total"][doc["_id"]["date"]] = doc["totalOrderCount"] + resultsTotalOrderCount[
            "total"].get(doc["_id"]["date"], 0)
        resultsTotalPriceRmb["total"][doc["_id"]["date"]] = doc["totalPriceRmb"] + resultsTotalPriceRmb["total"].get(
            doc["_id"]["date"], 0)

    days_ro = get_month_range(start_date["ro"])
    days_bg = get_month_range(start_date["bg"])
    days_hu = get_month_range(start_date["hu"])
    days_total = get_month_range(start_date["total"])
    result = {
        "total": {
            "yDate": days_total,
            "soldCount": [resultsTotalOrderCount['total'].get(i, 0) for i in days_total],
            "soldAmount": [round(resultsTotalPriceRmb['total'].get(i, 0), 0) for i in days_total],
        },
        "ro": {
            "yDate": days_ro,
            "soldCount": [resultsTotalOrderCount['ro'].get(i, 0) for i in days_ro],
            "soldAmount": [round(resultsTotalPriceRmb['ro'].get(i, 0), 0) for i in days_ro],
        },
        "bg": {
            "yDate": days_bg,
            "soldCount": [resultsTotalOrderCount['bg'].get(i, 0) for i in days_bg],
            "soldAmount": [round(resultsTotalPriceRmb['bg'].get(i, 0), 0) for i in days_bg],
        },
        "hu": {
            "yDate": days_hu,
            "soldCount": [resultsTotalOrderCount['hu'].get(i, 0) for i in days_hu],
            "soldAmount": [round(resultsTotalPriceRmb['hu'].get(i, 0), 0) for i in days_hu],
        },
    }
    return result


async def get_order_trency_per_year(campany_id, shop, order_status):
    collection_em_order: AsyncIOMotorCollection = app.ctx.mongo[EmOrder.collection_name]
    # 聚合管道
    pipeline = [
        {
            "$match": {
                "campanyId": campany_id,
                "status": {"$in": [int(i) for i in order_status]},
                "shop": shop
            }
        },
        {
            "$group": {
                "_id": {
                    "date": {
                        '$dateToString': {
                            'format': '%Y',
                            'date': '$date'
                        }
                    },
                    'country': '$country'
                },
                'totalOrderCount': {'$sum': 1},
                'totalPriceRmb': {'$sum': '$totalPriceRmb'},
            }
        },
        {
            '$project': {
                # 28zhou
                '_id': 1,
                'totalOrderCount': 1,
                'totalPriceRmb': 1
            }
        },
        {
            '$sort': {'_id': 1}
        }
    ]
    # 执行聚合查询
    resultsTotalOrderCount = {"ro": {}, "bg": {}, "hu": {}, "total": {}}
    resultsTotalPriceRmb = {"ro": {}, "bg": {}, "hu": {}, "total": {}}
    start_date = {"ro": None, "bg": None, "hu": None, "total": None}
    async for doc in collection_em_order.aggregate(pipeline):
        # 转换为更友好的格式
        if start_date[doc["_id"]["country"]] is None or (
                int(start_date[doc["_id"]["country"]].replace("-", "")) > int(doc["_id"]["date"].replace("-", ""))):
            start_date[doc["_id"]["country"]] = doc["_id"]["date"]
        if start_date["total"] is None or (
                int(start_date["total"].replace("-", "")) > int(doc["_id"]["date"].replace("-", ""))):
            start_date["total"] = doc["_id"]["date"]

        resultsTotalOrderCount[doc["_id"]["country"]][doc["_id"]["date"]] = doc["totalOrderCount"]
        resultsTotalPriceRmb[doc["_id"]["country"]][doc["_id"]["date"]] = doc["totalPriceRmb"]

        resultsTotalOrderCount["total"][doc["_id"]["date"]] = doc["totalOrderCount"] + resultsTotalOrderCount[
            "total"].get(doc["_id"]["date"], 0)
        resultsTotalPriceRmb["total"][doc["_id"]["date"]] = doc["totalPriceRmb"] + resultsTotalPriceRmb["total"].get(
            doc["_id"]["date"], 0)

    days_ro = get_year_range(start_date["ro"])
    days_bg = get_year_range(start_date["bg"])
    days_hu = get_year_range(start_date["hu"])
    days_total = get_year_range(start_date["total"])
    result = {
        "total": {
            "yDate": days_total,
            "soldCount": [resultsTotalOrderCount['total'].get(i, 0) for i in days_total],
            "soldAmount": [round(resultsTotalPriceRmb['total'].get(i, 0), 0) for i in days_total],
        },
        "ro": {
            "yDate": days_ro,
            "soldCount": [resultsTotalOrderCount['ro'].get(i, 0) for i in days_ro],
            "soldAmount": [round(resultsTotalPriceRmb['ro'].get(i, 0), 0) for i in days_ro],
        },
        "bg": {
            "yDate": days_bg,
            "soldCount": [resultsTotalOrderCount['bg'].get(i, 0) for i in days_bg],
            "soldAmount": [round(resultsTotalPriceRmb['bg'].get(i, 0), 0) for i in days_bg],
        },
        "hu": {
            "yDate": days_hu,
            "soldCount": [resultsTotalOrderCount['hu'].get(i, 0) for i in days_hu],
            "soldAmount": [round(resultsTotalPriceRmb['hu'].get(i, 0), 0) for i in days_hu],
        },
    }
    return result


async def get_stock_value(campany_id, shop):
    collection_msku_inventory_detail: AsyncIOMotorCollection = app.ctx.mongo[MskuInventoryDetail.collection_name]
    whId = await get_shop_whid(campany_id, shop)
    # 聚合管道
    pipeline = [
        {
            "$match": {
                "campanyId": campany_id,
                "whId": whId
            }
        },
        {
            "$group": {
                "_id": '$status',
                'count':{'$sum':1},
                'totalMskuFee': {'$sum': '$mskuFee'},
                'totalMskuHeadFee': {'$sum': '$mskuHeadFee'},
            }
        },
        {
            '$project': {
                # 28zhou
                '_id': 1,
                'count':1,
                'totalMskuFee': 1,
                'totalMskuHeadFee': 1
            }
        },
        {
            '$sort': {'_id': 1}
        }
    ]
    # "0:在库 1:售出 2:在途 3:入仓丢失 4:销毁"
    result = {0: {"count":0,"value":0}, 1: {"count":0,"value":0}, 2: {"count":0,"value":0}, 3: {"count":0,"value":0}, 4: {"count":0,"value":0}}
    async for doc in collection_msku_inventory_detail.aggregate(pipeline):
        result[doc['_id']]["count"] = doc["count"]
        result[doc['_id']]["value"] = doc["totalMskuFee"] + doc["totalMskuHeadFee"]
    return result
