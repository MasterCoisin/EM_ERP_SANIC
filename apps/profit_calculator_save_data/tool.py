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
@Date        ：2025-04-01 0:48 
-------------------------------------
'''

from motor.motor_asyncio import AsyncIOMotorCollection
from sanic import Sanic

from config.constant import APP_NAME
from models.profit_calculator_save_data import ProfitCalculatorSaveData

app = Sanic.get_app(APP_NAME)


async def get_profit_calculator_save_data(uuid, campany_id):
    collection: AsyncIOMotorCollection = app.ctx.mongo[ProfitCalculatorSaveData.collection_name]
    result = await collection.find_one({"uuid": uuid, "campanyId": campany_id})
    return result


async def profit_calculator_save_data_has_to_sku(uuid, campany_id):
    collection: AsyncIOMotorCollection = app.ctx.mongo[ProfitCalculatorSaveData.collection_name]
    result = await collection.update_one({"uuid": uuid, "campanyId": campany_id}, {"$set": {"hasToSku": True}})
    return result
