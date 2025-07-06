# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：sku_inventory_index.py
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
from apps.msku_inventory_detail.tool import count_status_by_batch
from apps.overseas_warehouse.tool import get_shop_whid
from apps.user.tool import get_user_campany_id_by_request
from config.bean import SuccessResponse, FailureResponse
from models.msku_inventory_index import MskuInventoryIndex
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update
from utils.auth import protected
from utils.mongo_tool import add_filter_in_filters

bp_msku_inventory_index = Blueprint("mskuInventoryIndex", url_prefix="mskuInventoryIndex")  # 创建蓝图


@bp_msku_inventory_index.post("/list")
@protected(permission=["mskuInventoryIndex:list"],needVip=True)
async def msku_inventory_index_list(request: Request):
    """
    查询店铺列表
    :param request:
    :return:
    """
    current_page, page_size, fields, filters, sorts = get_request_base_params(request)
    campany_id = await get_user_campany_id_by_request(request)
    seleted_shop = request.json.get("seleted_shop",None)
    whId = await get_shop_whid(campany_id,seleted_shop)
    filters = add_filter_in_filters(filters, "campanyId", campany_id)
    filters = add_filter_in_filters(filters, "whId", whId)
    data = await mongodb_list(collection_name=MskuInventoryIndex.collection_name, fields=fields, filters=filters,
                              sorts=sorts,
                              current_page=current_page, page_size=page_size)
    if data["data"]:
        eans = [i["ean"] for i in data["data"]]
        # ean基础情况
        ean_base_info = await get_data_base_info_by_eans(eans,campany_id)

        data["data"] = [{**i,**ean_base_info.get(i["ean"],{})} for i in data["data"]]
    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_msku_inventory_index.post("/create")
@protected(permission=["mskuInventoryIndex:create"],needVip=True)
async def msku_inventory_index_create(request: Request):
    """
    创建店铺
    :param request:
    :return:
    """
    data: dict = request.json
    campany_id = await get_user_campany_id_by_request(request)
    data["campanyId"] = campany_id
    is_ok, msg = await mongodb_create(collection_name=MskuInventoryIndex.collection_name, data=data,
                                      uni_field=["whId", "ean","campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_msku_inventory_index.post("/update")
@protected(permission=["mskuInventoryIndex:update"],needVip=True)
async def msku_inventory_index_update(request: Request):
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
    is_ok, msg = await mongodb_update(collection_name=MskuInventoryIndex.collection_name, data=update_data,
                                      uni_field=[id_field, "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())
