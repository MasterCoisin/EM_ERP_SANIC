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
@Date        ：2025-07-03 21:37 
-------------------------------------
'''
from motor.motor_asyncio import AsyncIOMotorCollection
from sanic import Sanic

from config.constant import APP_NAME
from models.root_analysis import rootAnalysis

app = Sanic.get_app(APP_NAME)


async def get_root_analysis_by_uuid(uuid, campany_id):
    collection: AsyncIOMotorCollection = app.ctx.mongo[rootAnalysis.collection_name]
    result = await collection.find_one({"uuid": uuid, "campanyId": campany_id},
                                       {"_id": 0, "updateTime": 0, "createTime": 0})
    return result
