# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：databoard.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-06-04 15:47 
-------------------------------------
'''
from sanic import Blueprint, json, Request

from apps.databoard.tool import get_order_trency
from apps.user.tool import get_user_campany_id_by_request
from config.bean import SuccessResponse, FailureResponse
from models.button import Button
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update
from utils.auth import protected

bp_databoard = Blueprint("databoard", url_prefix="databoard")  # 创建蓝图


@bp_databoard.post("/getDatabordData")
@protected(permission=[])
async def databoard_real_time_sold_count(request: Request):
    """
    实时单量
    :param request:
    :return:
    """
    campany_id = await get_user_campany_id_by_request(request)
    shop = request.json.get("shop","wl")
    order_status = request.json.get("order_status",['1','2','3','4','5'])
    chartData = await get_order_trency(campany_id, shop, order_status)
    return json(**SuccessResponse(message="OK", data=chartData).to_response())