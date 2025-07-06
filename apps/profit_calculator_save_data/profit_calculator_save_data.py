# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：profit_calculator_save_data.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024-12-19 21:52 
-------------------------------------
'''
import datetime

from loguru import logger
from sanic import Blueprint, json, Request

from apps.images.tool import image_id_to_url, url_to_id
from apps.profit_calculator_save_data.tool import get_profit_calculator_save_data, \
    profit_calculator_save_data_has_to_sku
from apps.sku_warehouse.tool import get_sku
from apps.user.tool import get_user_campany_id_by_request
from config.bean import SuccessResponse, FailureResponse
from models.product import Product
from models.profit_calculator_save_data import ProfitCalculatorSaveData
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update
from utils.auth import protected
from utils.common import get_uuid
from utils.mongo_tool import add_filter_in_filters

bp_profit_calculator_save_data = Blueprint("profitCalculatorSaveData", url_prefix="profitCalculatorSaveData")  # 创建蓝图


@bp_profit_calculator_save_data.post("/list")
@protected(permission=["profitCalculatorSaveDataManager:list"],needVip=True)
async def profit_calculator_save_data_list(request: Request):
    """
    :param request:
    :return:
    """
    current_page, page_size, fields, filters, sorts = get_request_base_params(request)
    if "createTime" not in [i["field"] for i in sorts]:
        sorts.append({"field":"createTime","t":"desc"})
    campany_id = await get_user_campany_id_by_request(request)
    filters = add_filter_in_filters(filters, "campanyId", campany_id)
    data = await mongodb_list(collection_name=ProfitCalculatorSaveData.collection_name, fields=fields, filters=filters,
                              sorts=sorts,
                              current_page=current_page, page_size=page_size)
    for s_d in data["data"]:
        s_d["images"] = [image_id_to_url(i) for i in s_d.get("images", [])]
    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_profit_calculator_save_data.post("/create")
@protected(permission=["profitCalculatorSaveDataManager:create"],needVip=True)
async def profit_calculator_save_data_create(request: Request):
    """
    :param request:
    :return:
    """
    data: dict = request.json
    data["uuid"] = get_uuid()
    campany_id = await get_user_campany_id_by_request(request)
    data["campanyId"] = campany_id
    data["images"] = url_to_id(data.get("images", []))
    is_ok, msg = await mongodb_create(collection_name=ProfitCalculatorSaveData.collection_name, data=data,
                                      uni_field=["uuid","campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_profit_calculator_save_data.post("/update")
@protected(permission=["profitCalculatorSaveDataManager:update"],needVip=True)
async def profit_calculator_save_data_update(request: Request):
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
    if "images" in update_data:update_data["images"] = url_to_id(update_data.get("images", []))
    is_ok, msg = await mongodb_update(collection_name=ProfitCalculatorSaveData.collection_name, data=update_data,
                                      uni_field=[id_field,"campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_profit_calculator_save_data.post('/to_sku')
@protected(permission=["productManager:create"],needVip=True)
async def profit_calculator_to_sku(request: Request):
    uuid = request.json.get('uuid', None)
    if uuid:
        campany_id = await get_user_campany_id_by_request(request)
        data = await get_profit_calculator_save_data(uuid=uuid,campany_id=campany_id)
        if not data:
            return json(**FailureResponse(message="转入失败", data={}).to_response())
        sku = await get_sku()
        await mongodb_create(collection_name=Product.collection_name, data={
            "sku":sku,"campanyId":campany_id,
            "productName": data.get("productName",None),
            "url1688": data.get("url1688",None),
            "images": data.get("images",[]),
            "tip": data.get("tip",None),
            "competitorUrls": data.get("competitorUrls",None),
            "length":  data.get("length",None),
            "width":data.get("width",None),
            "height": data.get("height",None),
            "weight":  data.get("weight",None),
            "volumeWeight": data.get("volumeWeight",None),
            "weighing": data.get("weighing",None),
            "supplierInfo": {
                "purchaseCost": data.get("purchaseCost",None),
                "purchaseTip": None,
                "skuInfoMap": None,
                "specId": None,
                "supplierId": None},

            "createTime": datetime.datetime.now(),
            "updateTime": datetime.datetime.now(),
            "deleted": False
        },
                             uni_field=["sku", "campanyId"])
        await profit_calculator_save_data_has_to_sku(uuid=uuid,campany_id=campany_id)
        return json(**SuccessResponse(message="转入成功", data={}).to_response())
    else:
        return json(**FailureResponse(message="转入失败", data={}).to_response())
