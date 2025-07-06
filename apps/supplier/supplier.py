# -*- coding: UTF-8 -*-
# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：supplier.py
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


from apps.product.tool.sku_map_1688 import SkuMap1688
from apps.user.tool import get_user_campany_id_by_request
from config.bean import SuccessResponse, FailureResponse
from models.supplier import Supplier
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update
from utils.auth import protected
from utils.common import get_uuid
from utils.mongo_tool import add_filter_in_filters

bp_supplier = Blueprint("supplier", url_prefix="supplier")  # 创建蓝图


@bp_supplier.post("/list")
@protected(permission=["supplierManager:list"],needVip=True)
async def supplier_list(request: Request):
    """
    查询店铺列表
    :param request:
    :return:
    """
    current_page, page_size, fields, filters, sorts = get_request_base_params(request)
    campany_id = await get_user_campany_id_by_request(request)
    filters = add_filter_in_filters(filters, "campanyId", campany_id)
    data = await mongodb_list(collection_name=Supplier.collection_name, fields=fields, filters=filters, sorts=sorts,
                              current_page=current_page, page_size=page_size)
    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_supplier.post("/create")
@protected(permission=["supplierManager:create"],needVip=True)
async def supplier_create(request: Request):
    """
    创建店铺
    :param request:
    :return:
    """
    data: dict = request.json
    campany_id = await get_user_campany_id_by_request(request)
    data["campanyId"] = campany_id
    data["uuid"] = get_uuid()
    is_ok, msg = await mongodb_create(collection_name=Supplier.collection_name, data=data, uni_field=["uuid","campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_supplier.post("/update")
@protected(permission=["supplierManager:update"],needVip=True)
async def supplier_update(request: Request):
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
    is_ok, msg = await mongodb_update(collection_name=Supplier.collection_name, data=update_data, uni_field=[id_field,"campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_supplier.post("/parse_sku_url")
@protected(needVip=True)
async def supplier_parse_sku_url(request: Request):
    """
    更新店铺
    :param request:
    :return:
    """
    url = request.json.get('url', None)
    campany_id = await get_user_campany_id_by_request(request)
    if url:
        data = await SkuMap1688.spider_1688_info_task(url,campany_id)
        if data:
            return json(**SuccessResponse(message="OK", data=data).to_response())
        return json(**FailureResponse(message="解析失败", data={}).to_response())
    return json(**FailureResponse(message="链接不能为空", data={}).to_response())

