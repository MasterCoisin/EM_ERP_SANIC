# -*- coding: UTF-8 -*-
'''
@Project     ：em_buy_carts_monitor_backen 
@File        ：tool.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-03-03 14:46 
-------------------------------------
'''
import time

from loguru import logger
from motor.motor_asyncio import AsyncIOMotorCollection
from sanic import Blueprint, json, Request, Sanic

from alipayApi.alipayTook import aliPayTool
from apps.campany.tool import get_campany_info_by_id
from models.order import Order
from models.sys_user import SysUser
from utils.id_creator import order_id_create
from config.constant import APP_NAME

app = Sanic.get_app(APP_NAME)


async def create_svip_order(campany_id, order_id, month, total_amount, unit_amount, open_id):
    collection: AsyncIOMotorCollection = app.ctx.mongo["order"]
    result = await collection.insert_one(
        {"campanyId": campany_id, "orderId": order_id, "expireTime": None, "month": month, "total_amount": total_amount,
         "status": 0, "tip": f"高级会员{month}个月,{unit_amount}x{month}={total_amount}元", "type": 1,
         "open_id": open_id})


async def create_vip_order(campany_id, order_id, month, total_amount, unit_amount, open_id):
    collection: AsyncIOMotorCollection = app.ctx.mongo["order"]
    result = await collection.insert_one(
        {"campanyId": campany_id, "orderId": order_id, "expireTime": None, "month": month, "total_amount": total_amount,
         "status": 0, "tip": f"选品会员{month}个月,{unit_amount}x{month}={total_amount}元", "type": 2,
         "open_id": open_id})


async def send_free_vip(campany_id, days, open_id):
    try:
        order_id = order_id_create()
        pay_t = int(time.time())
        campany_info = await get_campany_info_by_id(campanyId=campany_id)
        if campany_info.get("isVip", False) == False or (
                campany_info.get("expireTime", 0) is None or campany_info.get("expireTime", 0) < time.time()):
            role_start_date = pay_t
            role_expire_date = pay_t + 3600 * 24 * days
        else:
            role_start_date = campany_info.get("expireTime", 0)
            role_expire_date = campany_info.get("expireTime", 0) + 3600 * 24 * days
        collection_order: AsyncIOMotorCollection = app.ctx.mongo["order"]
        collection_campany: AsyncIOMotorCollection = app.ctx.mongo["campany"]
        await collection_campany.update_one({"campanyId": campany_id},
                                            {"$set": {"isVip": True, "expireTime": role_expire_date}})
        result = await collection_order.insert_one(
            {"campanyId": campany_id, "orderId": order_id, "expireTime": None, "days": days,
             "status": 1, "tip": f"免费赠送高级会员{days}天", "type": 0, "payTime": pay_t,
             "role_start_date": role_start_date,
             "role_expire_date": role_expire_date, "open_id": open_id})
        return True
    except Exception as e:
        logger.exception(e)
        return False


async def get_pay_satatus(order_id, campany_id):
    collection: AsyncIOMotorCollection = app.ctx.mongo["order"]
    result = await collection.find_one(
        {"campanyId": campany_id, "orderId": order_id}, {"status": 1})
    if result:
        return {"status": result.get("status", 0)}
    return {"status": 0}


async def prepare_order(campany_id, month, open_id, t=1):
    unit_amount = 299
    unit = "月"
    order_id = order_id_create()
    campany_info = await get_campany_info_by_id(campanyId=campany_id)
    if campany_info.get("isVip", False) == False or (
            campany_info.get("expireTime", 0) is None or campany_info.get("expireTime", 0) < time.time()):
        role_expire_date = int(time.time()) + 3600 * 24 * month * 31
    else:
        role_expire_date = campany_info.get("expireTime", 0) + 3600 * 24 * month * 31
    total_amount = unit_amount * month
    ali_pay_url = aliPayTool.api_alipay_trade_page_pay(subject=f"高级会员{month}个月",
                                                       out_trade_no=order_id,
                                                       total_amount=total_amount, qrcode_width=200)
    await create_svip_order(campany_id, order_id, month, total_amount, unit_amount, open_id)
    return {"ali_pay_url": ali_pay_url, "order_id": order_id, "role_expire_date": role_expire_date,
            "total_amount": total_amount, "unit_amount": unit_amount, "unit": unit}


async def pay_success(order_id):
    collection_order: AsyncIOMotorCollection = app.ctx.mongo["order"]
    collection_campany: AsyncIOMotorCollection = app.ctx.mongo["campany"]
    result = await collection_order.find_one(
        {"orderId": order_id, "status": 0})
    if result:
        pay_t = int(time.time())
        campany_info = await get_campany_info_by_id(campanyId=result.get("campanyId"))
        if campany_info.get("isVip", False) == False or (
                campany_info.get("expireTime", 0) is None or campany_info.get("expireTime", 0) < time.time()):
            role_start_date = pay_t
            role_expire_date = pay_t + 3600 * 24 * result.get("month", 1) * 31
        else:
            role_start_date = campany_info.get("expireTime", 0)
            role_expire_date = campany_info.get("expireTime", 0) + 3600 * 24 * result.get("month", 1) * 31
        await collection_order.update_one(
            {"orderId": order_id, "status": 0}, {
                "$set": {"status": 1, "payTime": pay_t, "role_start_date": role_start_date,
                         "role_expire_date": role_expire_date}})
        await collection_campany.update_one({"campanyId": result.get("campanyId")},
                                            {"$set": {"isVip": True, "expireTime": role_expire_date}})
