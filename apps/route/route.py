# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：route.py
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

from config.bean import SuccessResponse, FailureResponse
from models.route import Route
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update
from utils.auth import protected

bp_route = Blueprint("route", url_prefix="route")  # 创建蓝图


@bp_route.post("/list")
@protected(permission=["routeManager:list"])
async def route_list(request: Request):
    """
    查询路由列表
    :param request:
    :return:
    """
    current_page, page_size, fields, filters, sorts = get_request_base_params(request)
    data = await mongodb_list(collection_name=Route.collection_name, fields=fields, filters=filters, sorts=sorts,
                              current_page=current_page, page_size=page_size)
    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_route.post("/create")
@protected(permission=["routeManager:create"])
async def route_create(request: Request):
    """
    创建路由
    :param request:
    :return:
    """
    data: dict = request.json
    is_ok, msg = await mongodb_create(collection_name=Route.collection_name, data=data, uni_field=["path"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_route.post("/update")
@protected(permission=["routeManager:update"])
async def route_update(request: Request):
    """
    更新路由
    :param request:
    :return:
    """
    data: dict = request.json
    _id = data.get("id", None)
    id_field = data.get("id_field", "open_id")
    update_data = data.get("data", {})
    update_data[id_field] = _id
    is_ok, msg = await mongodb_update(collection_name=Route.collection_name, data=update_data, uni_field=[id_field])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())
