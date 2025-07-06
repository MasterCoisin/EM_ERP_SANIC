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

from config.constant import APP_NAME
from models.shop import Shop

app = Sanic.get_app(APP_NAME)


async def get_shop_all_token1688():
    collection: AsyncIOMotorCollection = app.ctx.mongo[Shop.collection_name]
    result = collection.find({"deleted": False}, {"shop_id": 1, "token1688": 1,"campanyId":1})
    shops = []
    for document in await result.to_list():
        shops.append(document)
    return shops


async def get_shop_1688_token(shop_id):
    collection: AsyncIOMotorCollection = app.ctx.mongo[Shop.collection_name]
    result = await collection.find_one({"shop_id": shop_id}, {"token1688": 1})
    return result.get("token1688", None)


async def get_shop_info(shop_id):
    collection: AsyncIOMotorCollection = app.ctx.mongo[Shop.collection_name]
    result = await collection.find_one({"shop_id": shop_id}, {"_id": 0})
    return result


async def update_shop_cookie(shop_id, cookie):
    data = await get_shop_info(shop_id)
    em_login_info = data.get("em_login_info", {})
    em_login_info["cookie"] = cookie
    await app.ctx.mongo[Shop.collection_name].update_one({"shop_id": shop_id},
                                                         {"$set": {"em_login_info": em_login_info}})


async def get_shop_em_hash(shop_id):
    collection: AsyncIOMotorCollection = app.ctx.mongo[Shop.collection_name]
    result = await collection.find_one({"shop_id": shop_id}, {"em_login_info": 1})
    return result.get("em_login_info", {}).get("hash", None)
