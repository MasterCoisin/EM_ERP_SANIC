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
@Date        ：2025-06-05 15:11 
-------------------------------------
'''
from motor.motor_asyncio import AsyncIOMotorCollection
from sanic import Sanic

from config.constant import APP_NAME
from models.overseas_warehouse import OverseasWarehouse

app = Sanic.get_app(APP_NAME)


async def get_shop_whid(campany_id, shop):
    collection: AsyncIOMotorCollection = app.ctx.mongo[OverseasWarehouse.collection_name]
    result = await collection.find_one({"campanyId": campany_id, "shop": shop}, {"whId": 1})
    return result.get("whId", None) if result else None
