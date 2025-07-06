# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：shipments_order.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-04-23 16:46 
-------------------------------------
'''
from loguru import logger
from sanic import Blueprint, json, Request

from apps.em_reception.tool import get_em_reception_emid_by_em_reception_ids
from apps.listing.tool import get_packing_data_by_ean
from apps.shipments_order.tool import get_shipments_order_by_shipments_order_id
from apps.sku_inventory_detail.tool import change_sku_status_for_shipments_order_inbound
from apps.user.tool import get_user_campany_id_by_request
from config.bean import SuccessResponse, FailureResponse
from models.shipments_order import ShipmentsOrder
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update
from utils.auth import protected
from utils.mongo_tool import add_filter_in_filters

bp_shipments_order = Blueprint("shipmentsOrder", url_prefix="shipmentsOrder")  # 创建蓝图


@bp_shipments_order.post("/list")
@protected(permission=["shipmentsOrderManager:list"], needVip=True)
async def shipments_order_list(request: Request):
    """
    :param request:
    :return:
    """
    current_page, page_size, fields, filters, sorts = get_request_base_params(request)
    seleted_shop = request.json.get("seleted_shop", "wl")
    campany_id = await get_user_campany_id_by_request(request)
    filters = add_filter_in_filters(filters, "campanyId", campany_id)
    if "createTime" not in [i["field"] for i in sorts]:
        sorts.append({"field": "createTime", "t": "desc"})
    data = await mongodb_list(collection_name=ShipmentsOrder.collection_name, fields=fields, filters=filters, sorts=sorts,
                              current_page=current_page, page_size=page_size,seleted_shop=seleted_shop)
    emReceptionIds = [i["emReceptionId"] for i in data["data"] if i.get("emReceptionId",None)]
    if emReceptionIds:
        res = await get_em_reception_emid_by_em_reception_ids(emReceptionIds,campany_id)
        for i in data["data"]:
            if i["status"]==5:
                i["totalDays"] = f'{round((i["updateTime"]-i["createTime"])/(3600*24),2)}天'
            elif i["status"]==4:
                i["totalDays"] = "查验中"
            else:
                i["totalDays"] = "运输中"
            if i.get("emReceptionId",None):
                i["receptionId"] = res.get(i.get("emReceptionId",None),None)
    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_shipments_order.post("/create")
@protected(permission=["shipmentsOrderManager:create"], needVip=True)
async def shipments_order_create(request: Request):
    """
    :param request:
    :return:
    """
    data: dict = request.json
    campany_id = await get_user_campany_id_by_request(request)
    data["campanyId"] = campany_id
    is_ok, msg = await mongodb_create(collection_name=ShipmentsOrder.collection_name, data=data,
                                      uni_field=["shipmentsOrderId", "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_shipments_order.post("/update")
@protected(permission=["shipmentsOrderManager:update"], needVip=True)
async def shipments_order_update(request: Request):
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
    if "status" in update_data and update_data["status"]==4:
        await change_sku_status_for_shipments_order_inbound(campany_id, update_data["shipmentsOrderId"])
    is_ok, msg = await mongodb_update(collection_name=ShipmentsOrder.collection_name, data=update_data,
                                      uni_field=[id_field, "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_shipments_order.post("/get")
@protected(permission=["shipmentsOrderManager:list"], needVip=True)
async def shipments_order_get(request: Request):
    """
    :param request:
    :return:
    """
    campany_id = await get_user_campany_id_by_request(request)
    shipmentsOrderId = request.json.get("shipmentsOrderId", None)
    if not shipmentsOrderId:
        return json(**FailureResponse(message="未找到面单", data={}).to_response())
    is_ok, data = await get_shipments_order_by_shipments_order_id(shipmentsOrderId=shipmentsOrderId, campany_id=campany_id)
    if is_ok:
        #
        for ean_info in data["eanInfo"]:
            is_ok, ean_data = await get_packing_data_by_ean(ean_info["ean"], campany_id)
            if type(ean_data) == dict:
                ean_info["images"] = ean_data["images"]
                ean_info["listingName"] = ean_data["listingName"]
        emReceptionId = data.get("emReceptionId", None)
        if emReceptionId:
            res = await get_em_reception_emid_by_em_reception_ids([emReceptionId], campany_id)
            data["receptionId"] = res.get(data.get("emReceptionId", None), None)
        return json(**SuccessResponse(message="OK", data=data).to_response())
    else:
        return json(**FailureResponse(message=data, data={}).to_response())

@bp_shipments_order.post("/inbound")
@protected(permission=["shipmentsOrderManager:update"], needVip=True)
async def shipments_order_inbound(request: Request):
    """
    :param request:
    :return:
    """
    campany_id = await get_user_campany_id_by_request(request)
    shipmentsOrderId = request.json.get("shipmentsOrderId", None)
    if not shipmentsOrderId:
        return json(**FailureResponse(message="未找到面单", data={}).to_response())
    is_ok, data = await change_sku_status_for_shipments_order_inbound(campany_id, shipmentsOrderId)
    if is_ok:
        return json(**SuccessResponse(message="OK", data=data).to_response())
    else:
        return json(**FailureResponse(message=data, data={}).to_response())

