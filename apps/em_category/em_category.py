# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：em_category.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-04-03 22:49 
-------------------------------------
'''
from loguru import logger
from sanic import Blueprint, json, Request

from apps.user.tool import get_user_campany_id_by_request
from config.bean import SuccessResponse, FailureResponse
from models.em_category import EmCategory
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update
from utils.auth import protected
from utils.common import get_hash
from utils.mongo_tool import add_filter_in_filters

bp_em_category = Blueprint("emCategory", url_prefix="emCategory")  # 创建蓝图


@bp_em_category.post("/list")
@protected(permission=["emCategoryManager:list"],needVip=True)
async def em_category_list(request: Request):
    """
    :param request:
    :return:
    """
    current_page, page_size, fields, filters, sorts = get_request_base_params(request)
    campany_id = await get_user_campany_id_by_request(request)
    data = await mongodb_list(collection_name=EmCategory.collection_name, fields=fields, filters=filters, sorts=sorts,
                              current_page=current_page, page_size=page_size)
    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_em_category.post("/create")
@protected(permission=["emCategoryManager:create"],needVip=True)
async def em_category_create(request: Request):
    """
    创建店铺
    :param request:
    :return:
    """
    data: dict = request.json
    if data.get("em_login_info", {}).get("username", None) and data.get("em_login_info", {}).get("password", None):
        data["em_login_info"]["hash"] = get_hash(
            data.get("em_login_info", {}).get("username", None) + ':' + data.get("em_login_info", {}).get("password",
                                                                                                          None))
    is_ok, msg = await mongodb_create(collection_name=EmCategory.collection_name, data=data,
                                      uni_field=["em_category_id", "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_em_category.post("/update")
@protected(permission=["emCategoryManager:update"],needVip=True)
async def em_category_update(request: Request):
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
    if update_data.get("em_login_info", {}).get("username", None) and update_data.get("em_login_info", {}).get(
            "password", None):
        update_data["em_login_info"]["hash"] = get_hash(
            update_data.get("em_login_info", {}).get("username", None) + ':' + update_data.get("em_login_info", {}).get(
                "password", None))
    is_ok, msg = await mongodb_update(collection_name=EmCategory.collection_name, data=update_data,
                                      uni_field=[id_field, "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())
