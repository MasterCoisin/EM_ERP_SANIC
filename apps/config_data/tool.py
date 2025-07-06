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
from models.config_data import ConfigData

app = Sanic.get_app(APP_NAME)


async def get_config_data_by_field_name(field_name):
    collection: AsyncIOMotorCollection = app.ctx.mongo[ConfigData.collection_name]
    result = await collection.find_one({"field_name": field_name}, {"data": 1})
    return result.get("data", None)



