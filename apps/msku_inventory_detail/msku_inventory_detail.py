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

from apps.listing.tool import get_data_base_info_by_eans
from apps.msku_inventory_detail.tool import get_today_in_trans
from apps.msku_inventory_index.tool import ean_inbount_losed, ean_destroyed
from apps.user.tool import get_user_campany_id_by_request
from config.bean import SuccessResponse, FailureResponse
from models.msku_inventory_detail import MskuInventoryDetail
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update
from utils.auth import protected
from utils.mongo_tool import add_filter_in_filters

bp_msku_inventory_detail = Blueprint("mskuInventoryDetail", url_prefix="mskuInventoryDetail")  # 创建蓝图


@bp_msku_inventory_detail.post("/list")
@protected(permission=["mskuInventoryDetail:list"], needVip=True)
async def msku_inventory_detail_list(request: Request):
    """
    查询店铺列表
    :param request:
    :return:
    """
    current_page, page_size, fields, filters, sorts = get_request_base_params(request)
    campany_id = await get_user_campany_id_by_request(request)
    filters = add_filter_in_filters(filters, "campanyId", campany_id)
    data = await mongodb_list(collection_name=MskuInventoryDetail.collection_name, fields=fields, filters=filters,
                              sorts=sorts,
                              current_page=current_page, page_size=page_size)
    if data["data"]:
        ean = data["data"][0]["ean"]
        ean_base_info = await get_data_base_info_by_eans([ean], campany_id)
        data["data"] = [{**i, **ean_base_info.get(i["ean"], {})} for i in data["data"]]
    for d in data["data"]:
        if "orderCreateDateTime" in d:
            del d["orderCreateDateTime"]
    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_msku_inventory_detail.post("/create")
@protected(permission=["mskuInventoryDetail:create"], needVip=True)
async def msku_inventory_detail_create(request: Request):
    """
    创建店铺
    :param request:
    :return:
    """
    data: dict = request.json
    campany_id = await get_user_campany_id_by_request(request)
    data["campanyId"] = campany_id
    is_ok, msg = await mongodb_create(collection_name=MskuInventoryDetail.collection_name, data=data,
                                      uni_field=["whId", "ean", "mskuBatchNumber", "mskuBatchOrder", "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_msku_inventory_detail.post("/update")
@protected(permission=["mskuInventoryDetail:update"], needVip=True)
async def msku_inventory_detail_update(request: Request):
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
    is_ok, msg = await mongodb_update(collection_name=MskuInventoryDetail.collection_name, data=update_data,
                                      uni_field=[id_field, "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_msku_inventory_detail.post("/inbountLosed")
@protected(permission=["mskuInventoryDetail:update"], needVip=True)
async def msku_inventory_detail_inbount_losed(request: Request):
    """
    :param request:
    :return:
    """
    data: dict = request.json
    campany_id = await get_user_campany_id_by_request(request)
    update_data = data
    update_data["campanyId"] = campany_id
    data["status"] = 3
    is_ok, msg = await mongodb_update(collection_name=MskuInventoryDetail.collection_name, data=update_data,
                                      uni_field=["ean", "whId", "mskuBatchNumber", "mskuBatchOrder", "campanyId"])
    result = await ean_inbount_losed(ean=data["ean"], campany_id=campany_id, wh_id=data["whId"], count=1)
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())

@bp_msku_inventory_detail.post("/destroyed")
@protected(permission=["mskuInventoryDetail:update"], needVip=True)
async def msku_inventory_detail_destroyed(request: Request):
    """
    :param request:
    :return:
    """
    data: dict = request.json
    campany_id = await get_user_campany_id_by_request(request)
    update_data = data
    update_data["campanyId"] = campany_id
    data["status"] = 4
    is_ok, msg = await mongodb_update(collection_name=MskuInventoryDetail.collection_name, data=update_data,
                                      uni_field=["ean", "whId", "mskuBatchNumber", "mskuBatchOrder", "campanyId"])
    result = await ean_destroyed(ean=data["ean"], campany_id=campany_id, wh_id=data["whId"], count=1)
    print(result)
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())

@bp_msku_inventory_detail.post("/updateTip")
@protected(permission=["mskuInventoryDetail:update"], needVip=True)
async def msku_inventory_detail_update_tip(request: Request):
    """
    :param request:
    :return:
    """
    data: dict = request.json
    campany_id = await get_user_campany_id_by_request(request)
    update_data = data
    update_data["campanyId"] = campany_id
    is_ok, msg = await mongodb_update(collection_name=MskuInventoryDetail.collection_name, data=update_data,
                                      uni_field=["ean", "whId", "mskuBatchNumber", "mskuBatchOrder", "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_msku_inventory_detail.post("/getTodayIntrans")
@protected(permission=["mskuInventoryDetail:list"], needVip=True)
async def msku_inventory_detail_get_today_in_trans(request: Request):
    """
    查询店铺列表
    :param request:
    :return:
    """
    campany_id = await get_user_campany_id_by_request(request)
    shop = request.json.get("shop","wl")
    data = await get_today_in_trans(campany_id,shop)
    return json(**SuccessResponse(message="OK", data=data).to_response())

