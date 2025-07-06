# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：emOrder.py
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

from apps.em_order.tool import parse_em_order_info, get_today_orders
from apps.images.tool import url_to_id, image_id_to_url
from apps.sku_inventory_index.tool import get_data_by_sku
from apps.sku_warehouse.tool import get_sku
from apps.user.tool import get_user_campany_id_by_request
from config.bean import SuccessResponse, FailureResponse
from models.em_order import EmOrder
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update
from utils.auth import protected
from utils.mongo_tool import add_filter_in_filters

bp_em_order = Blueprint("emOrderManager", url_prefix="emOrderManager")  # 创建蓝图


@bp_em_order.post("/list")
@protected(permission=["emOrderManager:list"], needVip=True)
async def em_order_list(request: Request):
    """
    :param request:
    :return:
    """
    current_page, page_size, fields, filters, sorts = get_request_base_params(request)
    seleted_shop = request.json.get("seleted_shop", "wl")
    if "date" not in [i["field"] for i in sorts]:
        sorts.append({"field": "date", "t": "desc"})
    campany_id = await get_user_campany_id_by_request(request)
    filters = [i for i in filters if i["field"]!="deleted"]
    filters = add_filter_in_filters(filters, "campanyId", campany_id)
    #
    for filter in filters:
        if filter["field"]=="orderId":
            filter["t"] = "eq"
            try:
                filter["value"] = int(filter["query"])
            except:
                filter["value"] = filter["query"]

    #
    data = await mongodb_list(collection_name=EmOrder.collection_name, fields=fields, filters=filters, sorts=sorts,
                              current_page=current_page, page_size=page_size, seleted_shop=seleted_shop)
    data["data"] = [await parse_em_order_info(i) for i in data["data"]]
    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_em_order.post("/create")
@protected(permission=["emOrderManager:create"], needVip=True)
async def em_order_create(request: Request):
    """
    创建产品
    :param request:
    :return:
    """
    data: dict = request.json
    campany_id = await get_user_campany_id_by_request(request)
    data["campanyId"] = campany_id
    is_ok, msg = await mongodb_create(collection_name=EmOrder.collection_name, data=data,
                                      uni_field=["orderId", "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_em_order.post("/update")
@protected(permission=["emOrderManager:update"], needVip=True)
async def em_order_update(request: Request):
    """
    更新产品
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
    is_ok, msg = await mongodb_update(collection_name=EmOrder.collection_name, data=update_data,
                                      uni_field=[id_field, "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())

@bp_em_order.post("/getTodayOrders")
@protected(permission=["emOrderManager:list"], needVip=True)
async def em_order_get_today_orders(request: Request):
    """
    :param request:
    :return:
    """
    shop = request.json.get("shop", "wl")
    campany_id = await get_user_campany_id_by_request(request)
    orders, mergeCells,ean_data,orderProfitData = await get_today_orders(campany_id, shop)
    return json(**SuccessResponse(message="OK", data={"orders":orders,"mergeCells":mergeCells,"eanDatas":ean_data,"orderProfitData":orderProfitData}).to_response())

