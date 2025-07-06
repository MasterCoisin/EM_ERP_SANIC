# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：mongo_tool.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024-11-18 0:44 
-------------------------------------
'''
from motor.motor_asyncio import AsyncIOMotorClient

from config.constant import MONGODB_URL


async def setup_db():
    return AsyncIOMotorClient(MONGODB_URL).EM_ERP_SANIC,AsyncIOMotorClient(MONGODB_URL).EM_DATA


def add_filter_in_filters(filters: list[dict], field, value):
    for filter_item in filters:
        if filter_item["field"] == field:
            return filters
    filters.append({"field": field, "t": "eq", "value": value})
    return filters