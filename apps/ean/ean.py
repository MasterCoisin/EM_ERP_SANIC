# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：ean.py
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

from apps.user.tool import get_user_campany_id_by_request
from config.bean import SuccessResponse, UnauthorizedResponse, FailureResponse
from models.ean import Ean
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update, \
    mongodb_create_batch
from utils.auth import protected
from utils.mongo_tool import add_filter_in_filters

bp_ean = Blueprint("ean", url_prefix="ean")  # 创建蓝图


@bp_ean.post("/list")
@protected(needVip=True)
async def ean_list(request: Request):
    """
    :param request:
    :return:
    """
    current_page, page_size, fields, filters, sorts = get_request_base_params(request)
    campany_id = await get_user_campany_id_by_request(request)
    filters = add_filter_in_filters(filters, "campanyId", campany_id)
    data = await mongodb_list(collection_name=Ean.collection_name, fields=fields, filters=filters, sorts=sorts,
                              current_page=current_page, page_size=page_size)
    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_ean.post("/create")
@protected(permission=["eanManager:create"],needVip=True)
async def ean_create(request: Request):
    """
    创建店铺
    :param request:
    :return:
    """
    data: dict = request.json
    campany_id = await get_user_campany_id_by_request(request)
    data["campanyId"] = campany_id
    is_ok, msg = await mongodb_create(collection_name=Ean.collection_name, data=data, uni_field=["ean","campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())
@bp_ean.post("/createBatch")
@protected(permission=["eanManager:create"],needVip=True)
async def ean_create_batch(request: Request):
    """
    :param request:
    :return:
    """
    data: dict = request.json
    campany_id = await get_user_campany_id_by_request(request)
    datas = [{"ean":ean,"campanyId":campany_id,"deleted":False} for ean in data.get("eans",[])]
    is_ok, msg = await mongodb_create_batch(collection_name=Ean.collection_name, datas=datas, uni_field=["ean","campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())

@bp_ean.post("/update")
@protected(permission=["eanManager:update"],needVip=True)
async def ean_update(request: Request):
    """
    更新店铺
    :param request:
    :return:
    """
    data: dict = request.json
    _id = data.get("id", None)
    campany_id = await get_user_campany_id_by_request(request)
    id_field = data.get("id_field", "open_id")
    update_data = data.get("data", {})
    update_data[id_field] = _id
    update_data["campanyId"] = campany_id
    is_ok, msg = await mongodb_update(collection_name=Ean.collection_name, data=update_data, uni_field=[id_field,"campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())
