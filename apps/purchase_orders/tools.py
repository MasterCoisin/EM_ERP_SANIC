# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：tools.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-02-06 16:49 
-------------------------------------
'''
import json

import aiohttp

from apps.shop.tool import get_shop_all_token1688
from config.constant import API_1688_HOST, API_1688_PORT
from motor.motor_asyncio import AsyncIOMotorCollection
from sanic import Sanic

from config.constant import APP_NAME

app = Sanic.get_app(APP_NAME)


async def init_address_one_shop(shop_id, token1688, campany_id):
    async with aiohttp.ClientSession() as session:
        url = f"http://{API_1688_HOST}:{API_1688_PORT}/api1688/init_address/"
        print(url)
        headers = {
            'Content-Type': 'application/json'
        }
        payload = {
            "shop_id": shop_id,
            "token1688": token1688,
            "campany_id": campany_id
        }
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("data", {})
    return {}


async def init_all_shop_address():
    shops = await get_shop_all_token1688()
    for shop in shops:
        if shop.get("token1688", None):
            await init_address_one_shop(shop.get("shop_id", None), shop.get("token1688", None),
                                        shop.get("campanyId", None))


async def get_1688_address(campany_id):
    # TODO
    async with aiohttp.ClientSession() as session:
        url = f"http://{API_1688_HOST}:{API_1688_PORT}/api1688/get_address/{campany_id}"
        print(url)
        headers = {}
        payload = {}
        async with session.get(url, headers=headers, data=payload) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("data", {})
    return {}


async def create_1688_order_auto(address_id, skus_data, tip_for_seller, token):
    async with aiohttp.ClientSession() as session:
        url = f"http://{API_1688_HOST}:{API_1688_PORT}/api1688/create_order/"
        print(url)
        headers = {
            'Content-Type': 'application/json'
        }
        payload = {
            "address_id": address_id,
            "skus_data": skus_data,
            "tip_for_seller": tip_for_seller,
            "token": token
        }
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("data", {})
    return {}


async def get_today_in_purchase_sku_info(campany_id):
    collection_purchase_orders: AsyncIOMotorCollection = app.ctx.mongo["purchase_orders"]
    data = await collection_purchase_orders.find({"campanyId": campany_id, "status": {"$in": [1, 2, 3]},"deleted":False}).to_list()
    resuls = []
    for item in data:
        purchaseOrderId = item.get("purchaseOrderId", None)
        order_data = item.get("orders", {}).values()
        for order in order_data:
            status = order.get("order_info", {}).get("status", 0)
            skus = order.get("skus", [])
            hasPay = status >= 2
            if status < 8 and not order.get("deleted",False):
                for sku_info in skus:
                    resuls.append({
                        "purchaseOrderId": purchaseOrderId,
                        "sku": sku_info.get("sku", None),
                        "images": sku_info.get("images", []),
                        "fee": round(sku_info.get("fee", None) / 100, 2) if sku_info.get("fee", None) else sku_info.get(
                            "fee", None),
                        "count": sku_info.get("count", None),
                        "hasPay": hasPay,
                        "status": status
                    })

    return resuls
