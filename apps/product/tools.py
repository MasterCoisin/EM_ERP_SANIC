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
@Date        ：2025-04-13 14:44 
-------------------------------------
'''
from motor.motor_asyncio import AsyncIOMotorCollection
from sanic import Sanic

from config.constant import APP_NAME
from models.product import Product

app = Sanic.get_app(APP_NAME)


async def get_data_by_skus(skus, campany_id):
    collection: AsyncIOMotorCollection = app.ctx.mongo[Product.collection_name]
    result = await collection.find({"sku": {"$in": skus}, "campanyId": campany_id},
                                   {"_id": 0, "sku": 1, "images": 1, "productName": 1, "supplierInfo": 1,
                                    "url1688": 1}).to_list()
    return {i["sku"]: i for i in result}


async def get_data_base_info_by_skus(skus, campany_id):
    collection: AsyncIOMotorCollection = app.ctx.mongo[Product.collection_name]
    result = await collection.find({"sku": {"$in": skus}, "campanyId": campany_id},
                                   {"_id": 0, "sku": 1, "images": 1, "productName": 1, "url1688": 1}).to_list()
    return {i["sku"]: i for i in result}
