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
@Date        ：2025-04-03 22:49 
-------------------------------------
'''
from motor.motor_asyncio import AsyncIOMotorCollection
from sanic import Sanic

from config.constant import APP_NAME
from models.em_category import EmCategory

app = Sanic.get_app(APP_NAME)

async def get_em_category_name(category_id):
    collection: AsyncIOMotorCollection = app.ctx.mongo[EmCategory.collection_name]
    result = await collection.find_one({"category_id": category_id}, {"name_ro": 1})

    return result.get("name_ro", None)
