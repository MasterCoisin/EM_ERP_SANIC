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
@Date        ：2025-05-07 11:34 
-------------------------------------
'''

from motor.motor_asyncio import AsyncIOMotorCollection
from sanic import Sanic

from config.constant import APP_NAME
from models.shipments_order import ShipmentsOrder
from utils.common import datatime_to_timesmap

app = Sanic.get_app(APP_NAME)


async def get_shipments_order_by_shipments_order_id(shipmentsOrderId, campany_id):
    collection: AsyncIOMotorCollection = app.ctx.mongo[ShipmentsOrder.collection_name]
    result = await collection.find_one(
        {"shipmentsOrderId": shipmentsOrderId, "campanyId": campany_id, "deleted": False},
        {"_id": 0})
    if result:
        result = datatime_to_timesmap(result)
        return True, result
    else:
        return False, "未找到发货单"
