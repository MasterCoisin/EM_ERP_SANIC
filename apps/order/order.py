# -*- coding: UTF-8 -*-
'''
@Project     ：em_buy_carts_monitor_backen 
@File        ：order.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-03-03 14:42 
-------------------------------------
'''
from loguru import logger

from apps.order.tool import prepare_order, get_pay_satatus
from apps.user.tool import get_user_info_in_db, get_user_campany_id_by_request
from config.bean import SuccessResponse, FailureResponse
from models.order import Order
from mongodb_tool.db_list import get_request_base_params, mongodb_list
from sanic import Blueprint, json, Request
from utils.auth import protected
from utils.auth_tool import get_openid_from_token

bp_order = Blueprint("order", url_prefix="order")  # 创建蓝图


@bp_order.post("/prepare")
@protected()
async def order_prepare(request: Request):
    campany_id = await get_user_campany_id_by_request(request)
    open_id = get_openid_from_token(request)
    month = request.json.get("month", None)
    if not month:
        return json(**FailureResponse(message="参数不完整").to_response())
    data = await prepare_order(campany_id, month,open_id)
    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_order.post("/payStatus")
@protected()
async def order_pay_status(request: Request):
    campany_id = await get_user_campany_id_by_request(request)
    order_id = request.json.get("order_id", None)
    if not order_id:
        return json(**FailureResponse(message="参数不完整").to_response())
    data = await get_pay_satatus(order_id, campany_id)
    return json(**SuccessResponse(message="OK", data=data).to_response())
