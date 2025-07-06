# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：gprs_laws.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024-12-19 21:52 
-------------------------------------
'''
from sanic import Blueprint, json, Request

from apps.gprs_laws.tool import get_data_by_law_ids, gprs_search
from config.bean import SuccessResponse, FailureResponse
from models.gprs_laws import GprsLaws
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update
from utils.auth import protected
from utils.common import get_hash
from utils.mongo_tool import add_filter_in_filters

bp_gprs_laws = Blueprint("gprsLaws", url_prefix="gprsLaws")  # 创建蓝图


@bp_gprs_laws.post("/list")
@protected(needVip=True)
async def gprs_laws_list(request: Request):
    """
    查询店铺列表
    :param request:
    :return:
    """
    current_page, page_size, fields, filters, sorts = get_request_base_params(request)
    data = await mongodb_list(collection_name=GprsLaws.collection_name, fields=fields, filters=filters, sorts=sorts,
                              current_page=current_page, page_size=page_size)
    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_gprs_laws.post("/create")
@protected(needVip=True)
async def gprs_laws_create(request: Request):
    """
    创建店铺
    :param request:
    :return:
    """
    data: dict = request.json
    is_ok, msg = await mongodb_create(collection_name=GprsLaws.collection_name, data=data,
                                      uni_field=["lawId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_gprs_laws.post("/update")
@protected(needVip=True)
async def gprs_laws_update(request: Request):
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
    is_ok, msg = await mongodb_update(collection_name=GprsLaws.collection_name, data=update_data,
                                      uni_field=[id_field])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_gprs_laws.post("/getBylawId")
@protected(needVip=True)
async def gprs_laws_get_by_law_id(request: Request):
    """
    查询店铺列表
    :param request:
    :return:
    """
    law_ids = request.json.get("lawIds",[])
    if not law_ids:
        return json(**SuccessResponse(message="OK", data=[]).to_response())
    data = await get_data_by_law_ids(law_ids)
    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_gprs_laws.post("/gprsSearch")
@protected(needVip=True)
async def gprs_laws_gprs_search(request: Request):
    """
    查询店铺列表
    :param request:
    :return:
    """
    query = request.json.get("query",None)
    data = await gprs_search(query)
    return json(**SuccessResponse(message="OK", data=data).to_response())