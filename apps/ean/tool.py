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
@Date        ：2025-04-05 12:43 
-------------------------------------
'''
from motor.motor_asyncio import AsyncIOMotorCollection
from sanic import Sanic

from config.constant import APP_NAME
from models.ean import Ean

app = Sanic.get_app(APP_NAME)


async def get_ean(campany_id):
    collection: AsyncIOMotorCollection = app.ctx.mongo[Ean.collection_name]
    result = await collection.find_one({"campanyId": campany_id,"deleted":False}, {"ean": 1})
    print(result)
    if result:
        await collection.update_one({"campanyId": campany_id, "ean": result.get("ean",None)}, {"$set": {"deleted":True}})
        return result.get("ean",None)
    return None