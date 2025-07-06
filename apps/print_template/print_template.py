# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：print_template.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-04-14 14:04 
-------------------------------------
'''
from loguru import logger
from sanic import Blueprint, json, Request

from apps.user.tool import get_user_campany_id_by_request
from config.bean import SuccessResponse, FailureResponse
from models.print_template import PrintTemplate
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update
from utils.auth import protected
from utils.common import get_hash, get_uuid
from utils.mongo_tool import add_filter_in_filters

bp_print_template = Blueprint("printTemplate", url_prefix="printTemplate")  # 创建蓝图


@bp_print_template.post("/list")
@protected(permission=["printTemplateManager:list"],needVip=True)
async def print_template_list(request: Request):
    """
    查询店铺列表
    :param request:
    :return:
    """
    current_page, page_size, fields, filters, sorts = get_request_base_params(request)
    campany_id = await get_user_campany_id_by_request(request)
    filters = add_filter_in_filters(filters, "campanyId", campany_id)

    data = await mongodb_list(collection_name=PrintTemplate.collection_name, fields=fields, filters=filters, sorts=sorts,
                              current_page=current_page, page_size=page_size)
    # 解析长和宽
    for d in data["data"]:
        try:
            d["width"]=d["template"]["panels"][0]["width"]
            d["height"] = d["template"]["panels"][0]["height"]
        except Exception as e:
            pass
    #
    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_print_template.post("/create")
@protected(permission=["printTemplateManager:create"],needVip=True)
async def print_template_create(request: Request):
    """
    创建店铺
    :param request:
    :return:
    """
    data: dict = request.json
    campany_id = await get_user_campany_id_by_request(request)
    data["campanyId"] = campany_id
    data["printTemplateId"] = get_uuid()
    is_ok, msg = await mongodb_create(collection_name=PrintTemplate.collection_name, data=data,
                                      uni_field=["printTemplateId", "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_print_template.post("/update")
@protected(permission=["printTemplateManager:update"],needVip=True)
async def print_template_update(request: Request):
    """
    更新店铺
    :param request:
    :return:
    """
    data: dict = request.json
    campany_id = await get_user_campany_id_by_request(request)
    _id = data.get("id", None)
    id_field = data.get("id_field", "open_id")
    update_data = data.get("data", {})
    update_data[id_field] = _id
    update_data["campanyId"] = campany_id
    is_ok, msg = await mongodb_update(collection_name=PrintTemplate.collection_name, data=update_data,
                                      uni_field=[id_field, "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())
