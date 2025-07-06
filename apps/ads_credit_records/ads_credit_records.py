# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：ads_credit_records.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-06-19 15:29 
-------------------------------------
'''
from sanic import Blueprint, json, Request

from apps.user.tool import get_user_campany_id_by_request
from config.bean import SuccessResponse, FailureResponse
from models.ads_credit_records import adsCreditRecords
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update
from utils.auth import protected
from utils.mongo_tool import add_filter_in_filters

bp_ads_credit_records = Blueprint("adsCreditRecords", url_prefix="adsCreditRecords")  # 创建蓝图


@bp_ads_credit_records.post("/list")
@protected(permission=["adsCreditRecords:list"], needVip=True)
async def ads_credit_records_list(request: Request):
    """
    :param request:
    :return:
    """
    current_page, page_size, fields, filters, sorts = get_request_base_params(request)
    seleted_shop = request.json.get("seleted_shop", "wl")
    if "activationDate" not in [i["field"] for i in sorts]:
        sorts.append({"field": "date", "t": "desc"})
    campany_id = await get_user_campany_id_by_request(request)
    filters = [i for i in filters if i["field"]!="deleted"]
    filters = add_filter_in_filters(filters, "campanyId", campany_id)
    #
    data = await mongodb_list(collection_name=adsCreditRecords.collection_name, fields=fields, filters=filters, sorts=sorts,
                              current_page=current_page, page_size=page_size, seleted_shop=seleted_shop)
    for i in data["data"]:
        for f in ["activationDate","expirationDate"]:
            if i.get(f,None):
                i[f] = i[f].timestamp()
    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_ads_credit_records.post("/create")
@protected(permission=["adsCreditRecords:create"], needVip=True)
async def ads_credit_records_create(request: Request):
    """
    :param request:
    :return:
    """
    data: dict = request.json
    campany_id = await get_user_campany_id_by_request(request)
    data["campanyId"] = campany_id
    is_ok, msg = await mongodb_create(collection_name=adsCreditRecords.collection_name, data=data,
                                      uni_field=["creditId", "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_ads_credit_records.post("/update")
@protected(permission=["adsCreditRecords:update"], needVip=True)
async def ads_credit_records_update(request: Request):
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
    is_ok, msg = await mongodb_update(collection_name=adsCreditRecords.collection_name, data=update_data,
                                      uni_field=[id_field, "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())
