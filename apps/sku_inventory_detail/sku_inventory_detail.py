# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：sku_inventory_detail.py
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

from apps.product.tools import get_data_base_info_by_skus
from apps.sku_inventory_index.tool import sku_deal_by_self
from apps.user.tool import get_user_campany_id_by_request
from config.bean import SuccessResponse, FailureResponse
from models.sku_inventory_detail import SkuInventoryDetail
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update
from utils.auth import protected
from utils.mongo_tool import add_filter_in_filters

bp_sku_inventory_detail = Blueprint("skuInventoryDetail", url_prefix="skuInventoryDetail")  # 创建蓝图


@bp_sku_inventory_detail.post("/list")
@protected(permission=["skuInventoryDetail:list"])
async def sku_inventory_detail_list(request: Request):
    """
    :param request:
    :return:
    """
    current_page, page_size, fields, filters, sorts = get_request_base_params(request)
    campany_id = await get_user_campany_id_by_request(request)
    filters = add_filter_in_filters(filters, "campanyId", campany_id)
    data = await mongodb_list(collection_name=SkuInventoryDetail.collection_name, fields=fields, filters=filters,
                              sorts=sorts,
                              current_page=current_page, page_size=page_size)
    if data["data"]:
        sku = data["data"][0]["sku"]
        sku_base_info = await get_data_base_info_by_skus([sku],campany_id)
        data["data"] = [{**i,**sku_base_info.get(sku,{})} for i in data["data"]]
    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_sku_inventory_detail.post("/create")
@protected(permission=["skuInventoryDetail:create"],needVip=True)
async def sku_inventory_detail_create(request: Request):
    """
    创建店铺
    :param request:
    :return:
    """
    data: dict = request.json
    campany_id = await get_user_campany_id_by_request(request)
    data["campanyId"] = campany_id
    is_ok, msg = await mongodb_create(collection_name=SkuInventoryDetail.collection_name, data=data,
                                      uni_field=["whId", "sku", "skuBatchNumber", "skuBatchOrder", "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_sku_inventory_detail.post("/update")
@protected(permission=["skuInventoryDetail:update"],needVip=True)
async def sku_inventory_detail_update(request: Request):
    """
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
    is_ok, msg = await mongodb_update(collection_name=SkuInventoryDetail.collection_name, data=update_data,
                                      uni_field=[id_field, "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_sku_inventory_detail.post("/dealByself")
@protected(permission=["skuInventoryDetail:update"],needVip=True)
async def sku_inventory_detail_deal_by_self(request: Request):
    """
    :param request:
    :return:
    """
    data: dict = request.json
    skuStatus = 4
    campany_id = await get_user_campany_id_by_request(request)
    update_data = data
    update_data["campanyId"] = campany_id
    data["skuStatus"] = skuStatus
    is_ok, msg = await mongodb_update(collection_name=SkuInventoryDetail.collection_name, data=update_data,
                                      uni_field=["sku", "whId", "skuBatchNumber", "skuBatchOrder", "campanyId"])
    result = await sku_deal_by_self(sku=data["sku"],campany_id=campany_id,wh_id=data["whId"],count=1)
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())

@bp_sku_inventory_detail.post("/updateTip")
@protected(permission=["skuInventoryDetail:update"],needVip=True)
async def sku_inventory_detail_update_tip(request: Request):
    """
    :param request:
    :return:
    """
    data: dict = request.json
    campany_id = await get_user_campany_id_by_request(request)
    update_data = data
    update_data["campanyId"] = campany_id
    is_ok, msg = await mongodb_update(collection_name=SkuInventoryDetail.collection_name, data=update_data,
                                      uni_field=["sku", "whId", "skuBatchNumber", "skuBatchOrder", "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())