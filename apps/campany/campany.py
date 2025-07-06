# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：campany.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024-12-19 21:52 
-------------------------------------
'''
from loguru import logger
from sanic import Blueprint, json, Request

from apps.order.tool import send_free_vip
from apps.user.tool import get_user_campany_id_by_request
from config.bean import SuccessResponse, FailureResponse
from models.campany import Campany
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update
from utils.auth import protected
from utils.auth_tool import get_openid_from_token

bp_campany = Blueprint("campany", url_prefix="campany")  # 创建蓝图


@bp_campany.post("/list")
@protected(permission=["campanyManager:list"],needVip=True)
async def campany_list(request: Request):
    """
    查询店铺列表
    :param request:
    :return:
    """
    current_page, page_size, fields, filters, sorts = get_request_base_params(request)
    data = await mongodb_list(collection_name=Campany.collection_name, fields=fields, filters=filters, sorts=sorts,
                              current_page=current_page, page_size=page_size)
    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_campany.post("/create")
@protected(permission=["campanyManager:create"],needVip=True)
async def campany_create(request: Request):
    """
    创建店铺
    :param request:
    :return:
    """
    data: dict = request.json
    is_ok, msg = await mongodb_create(collection_name=Campany.collection_name, data=data,
                                      uni_field=["campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_campany.post("/update")
@protected(permission=["campanyManager:update"],needVip=True)
async def campany_update(request: Request):
    """
    更新店铺
    :param request:
    :return:
    """
    data: dict = request.json
    _id = data.get("id", None)
    id_field = data.get("id_field", "open_id")
    update_data = data.get("data", {})
    update_data[id_field] = _id
    is_ok, msg = await mongodb_update(collection_name=Campany.collection_name, data=update_data,
                                      uni_field=[id_field])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())

@bp_campany.post("/sendFreeVip")
@protected(permission=["campanyManager:update"],needVip=True)
async def campany_send_free_vip(request: Request):
    """
    :param request:
    :return:
    """
    data: dict = request.json
    open_id = get_openid_from_token(request)
    campany_id = data.get("campanyId", None)
    days = data.get("days", None)
    is_ok = await send_free_vip(campany_id, days,open_id)
    if is_ok:
        return json(**SuccessResponse(message="赠送成功", data={}).to_response())
    else:
        return json(**FailureResponse(message="赠送失败", data={}).to_response())
