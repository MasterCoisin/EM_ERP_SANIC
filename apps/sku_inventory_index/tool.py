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
from models.sku_inventory_index import SkuInventoryIndex

app = Sanic.get_app(APP_NAME)


async def get_data_by_sku(skus: list,campany_id):
    collection: AsyncIOMotorCollection = app.ctx.mongo[SkuInventoryIndex.collection_name]
    result = collection.find({"sku": {"$in": skus},"campanyId":campany_id}, {"_id": 0, "whId": 0}).to_list()
    return result


async def get_full_data_by_sku(sku,campany_id,wh_id):
    collection: AsyncIOMotorCollection = app.ctx.mongo[SkuInventoryIndex.collection_name]
    result = await collection.find_one({"sku": sku,"campanyId":campany_id,"whId":wh_id}, {"_id": 0})
    return result

async def sku_deal_by_self(sku,campany_id,wh_id,count):
    collection: AsyncIOMotorCollection = app.ctx.mongo[SkuInventoryIndex.collection_name]
    query = {
        "sku": sku,
        "campanyId": campany_id,  # 确保字段名与数据库完全一致
        "whId": wh_id
    }

    # 原子操作: skuLeft 减1
    update = {"$inc": {"skuLeft": -count,"skuDealByUs":count}}

    # 执行更新并返回更新后的文档
    result = await collection.find_one_and_update(
        query,
        update
    )
    return result
