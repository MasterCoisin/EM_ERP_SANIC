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
from models.msku_inventory_index import MskuInventoryIndex

app = Sanic.get_app(APP_NAME)


async def get_data_by_ean(eans: list):
    collection: AsyncIOMotorCollection = app.ctx.mongo[MskuInventoryIndex.collection_name]
    result = collection.find({"ean": {"$in": eans}}, {"_id": 0, "whId": 0}).to_list()
    return result


async def ean_inbount_losed(ean, campany_id, wh_id, count):
    collection: AsyncIOMotorCollection = app.ctx.mongo[MskuInventoryIndex.collection_name]
    query = {
        "ean": ean,
        "campanyId": campany_id,  # 确保字段名与数据库完全一致
        "whId": wh_id
    }

    # 原子操作: skuLeft 减1
    update = {"$inc": {"mskuLeft": -count, "mskuHasLosed": count}}

    # 执行更新并返回更新后的文档
    result = await collection.find_one_and_update(
        query,
        update
    )
    return result


async def ean_destroyed(ean, campany_id, wh_id, count):
    collection: AsyncIOMotorCollection = app.ctx.mongo[MskuInventoryIndex.collection_name]
    query = {
        "ean": ean,
        "campanyId": campany_id,  # 确保字段名与数据库完全一致
        "whId": wh_id
    }

    # 原子操作: skuLeft 减1
    update = {"$inc": {"mskuLeft": -count, "mskuHasDestroyed": count}}

    # 执行更新并返回更新后的文档
    result = await collection.find_one_and_update(
        query,
        update
    )
    return result
