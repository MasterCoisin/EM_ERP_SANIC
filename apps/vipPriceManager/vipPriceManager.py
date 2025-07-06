# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：vipPriceManager.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-06-17 21:59 
-------------------------------------
'''
from loguru import logger
from sanic import Blueprint, json, Request

from config.bean import SuccessResponse, FailureResponse
from models.vip_price import VipPriceManager
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update
from utils.auth import protected, role_permission
from utils.common import get_uuid
from utils.mongo_tool import add_filter_in_filters

bp_vip_price = Blueprint("vipPrice", url_prefix="vipPrice")  # 创建蓝图


@bp_vip_price.post("/list")
@protected(permission=[])
async def vip_price_list(request: Request):
    """
    :param request:
    :return:
    """
    current_page, page_size, fields, filters, sorts = get_request_base_params(request)
    for filed in ["vipType","index"]:
        if filed not in [i["field"] for i in sorts]:
            sorts.append({"field": filed, "t": "asc"})
    data = await mongodb_list(collection_name=VipPriceManager.collection_name, fields=fields, filters=filters, sorts=sorts,
                              current_page=current_page, page_size=page_size)
    for i in data["data"]:
        i["discount"] = round(10*i["price"]/i["orgPrice"],1)
    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_vip_price.post("/create")
@protected(permission=["vipPriceManager:create"])
async def vip_price_create(request: Request):
    """
    创建路由
    :param request:
    :return:
    """
    data: dict = request.json
    data["uuid"] = get_uuid()
    is_ok, msg = await mongodb_create(collection_name=VipPriceManager.collection_name, data=data, uni_field=["uuid"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_vip_price.post("/update")
@protected(permission=["vipPriceManager:update"])
async def vip_price_update(request: Request):
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
    is_ok, msg = await mongodb_update(collection_name=VipPriceManager.collection_name, data=update_data,
                                      uni_field=[id_field])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())
