# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：config_data.py
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
from models.config_data import ConfigData
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update
from utils.auth import protected

bp_config_data = Blueprint("configData", url_prefix="configData")  # 创建蓝图


@bp_config_data.post("/list")
@protected(permission=["configDataManager:list"])
async def config_data_list(request: Request):
    """
    :param request:
    :return:
    """
    current_page, page_size, fields, filters, sorts = get_request_base_params(request)
    if "priority" not in [i["field"] for i in sorts]:
        sorts.append({"field":"priority","t":"asc"})
    data = await mongodb_list(collection_name=ConfigData.collection_name, fields=fields, filters=filters, sorts=sorts,
                              current_page=current_page, page_size=page_size)
    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_config_data.post("/create")
@protected(permission=["configDataManager:create"])
async def config_data_create(request: Request):
    """
    创建店铺
    :param request:
    :return:
    """
    data: dict = request.json
    if "children" in data:
        del data["children"]
    is_ok, msg = await mongodb_create(collection_name=ConfigData.collection_name, data=data, uni_field=["field_name"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_config_data.post("/update")
@protected(permission=["configDataManager:update"])
async def config_data_update(request: Request):
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
    is_ok, msg = await mongodb_update(collection_name=ConfigData.collection_name, data=update_data, uni_field=[id_field])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())
