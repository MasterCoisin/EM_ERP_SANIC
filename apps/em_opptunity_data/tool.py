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
@Date        ：2025-06-13 9:54 
-------------------------------------
'''
from motor.motor_asyncio import AsyncIOMotorCollection
from sanic import Sanic
from config.constant import APP_NAME

app = Sanic.get_app(APP_NAME)


async def get_opp_data_version():
    collection: AsyncIOMotorCollection = app.ctx.mongo_em_data["opp_data_version"]
    result = collection.find({"status": 3}, {"_id": 0}).sort("version", direction=-1)
    versions = []
    for document in await result.to_list():
        versions.append(str(int(document.get("version", None))))
    return versions
