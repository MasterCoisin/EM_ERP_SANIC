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
@Date        ：2025-04-01 0:55 
-------------------------------------
'''
from motor.motor_asyncio import AsyncIOMotorCollection
from sanic import Sanic

from config.constant import APP_NAME
from models.sku_warehouse import SkuWarehouse

app = Sanic.get_app(APP_NAME)


async def get_sku():
    collection: AsyncIOMotorCollection = app.ctx.mongo[SkuWarehouse.collection_name]
    result = await collection.find_one_and_delete({})
    return result.get("sku",None)
