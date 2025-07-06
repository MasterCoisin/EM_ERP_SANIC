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
@Date        ：2025-04-12 16:45 
-------------------------------------
'''
import aiohttp

from motor.motor_asyncio import AsyncIOMotorCollection
from sanic import Sanic

from config.constant import APP_NAME
from models.gprs_laws import GprsLaws

app = Sanic.get_app(APP_NAME)


async def gprs_search(query):
    async with aiohttp.ClientSession() as session:
        url = f"http://127.0.0.1:9093/api/gprs/search/"
        print(url)
        headers = {
            'Content-Type': 'application/json'
        }
        payload = {
            "query": query,
        }
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("data", {})
    return []


async def get_data_by_law_ids(law_ids):
    collection: AsyncIOMotorCollection = app.ctx.mongo[GprsLaws.collection_name]
    result = await collection.find({"lawId": {"$in": law_ids}},
                                   {"_id": 0, "lawId": 1, "lawText": 1, "lawTextZh": 1}).to_list()
    return result
