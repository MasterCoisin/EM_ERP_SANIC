# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：em_reception.py
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

from apps.em_reception.tool import get_em_reception_by_em_reception_id, form_em_reception_excel, change_ean_status, \
    create_shipments_order
from apps.listing.tool import get_packing_data_by_ean
from apps.product.tool.sku_map_1688 import SkuMap1688
from apps.user.tool import get_user_campany_id_by_request
from config.bean import SuccessResponse, FailureResponse
from models.em_reception import EmReception
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update
from utils.auth import protected
from utils.common import get_uuid
from utils.mongo_tool import add_filter_in_filters

bp_em_reception = Blueprint("emReception", url_prefix="emReception")  # 创建蓝图


@bp_em_reception.post("/list")
@protected(permission=["emReceptionManager:list"], needVip=True)
async def em_reception_list(request: Request):
    """
    查询店铺列表
    :param request:
    :return:
    """
    current_page, page_size, fields, filters, sorts = get_request_base_params(request)
    seleted_shop = request.json.get("seleted_shop", "wl")
    campany_id = await get_user_campany_id_by_request(request)
    filters = add_filter_in_filters(filters, "campanyId", campany_id)
    if "createTime" not in [i["field"] for i in sorts]:
        sorts.append({"field": "createTime", "t": "desc"})
    data = await mongodb_list(collection_name=EmReception.collection_name, fields=fields, filters=filters, sorts=sorts,
                              current_page=current_page, page_size=page_size,seleted_shop=seleted_shop)
    for d in data["data"]:
        d["eanTypeCount"] = len(d["eanInfo"])
        eanCount = 0
        hasUpload = 0
        uploadError = 0
        unUpload = 0
        for ean_info in d["eanInfo"]:
            eanCount += ean_info.get("count", 0)
            uploadStatus = ean_info.get("uploadStatus", 0)
            if uploadStatus == 0:
                unUpload += 1
            elif uploadStatus == 1:
                hasUpload += 1
            elif uploadStatus == 2:
                uploadError += 1
        d["eanCount"] = eanCount
        d["hasUpload"] = hasUpload
        d["uploadError"] = uploadError
        d["unUpload"] = unUpload
        try:
            del d["eanInfo"]
        except:
            pass
    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_em_reception.post("/create")
@protected(permission=["emReceptionManager:create"], needVip=True)
async def em_reception_create(request: Request):
    """
    :param request:
    :return:
    """
    data: dict = request.json
    campany_id = await get_user_campany_id_by_request(request)
    data["campanyId"] = campany_id
    is_ok, msg = await mongodb_create(collection_name=EmReception.collection_name, data=data,
                                      uni_field=["emReceptionId", "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_em_reception.post("/update")
@protected(permission=["emReceptionManager:update"], needVip=True)
async def em_reception_update(request: Request):
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
    is_ok, msg = await mongodb_update(collection_name=EmReception.collection_name, data=update_data,
                                      uni_field=[id_field, "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_em_reception.post("/get")
@protected(permission=["emReceptionManager:list"], needVip=True)
async def em_reception_get(request: Request):
    """
    更新店铺
    :param request:
    :return:
    """
    campany_id = await get_user_campany_id_by_request(request)
    emReceptionId = request.json.get("emReceptionId", None)
    if not emReceptionId:
        return json(**FailureResponse(message="未找到面单", data={}).to_response())
    is_ok, data = await get_em_reception_by_em_reception_id(em_reception_id=emReceptionId, campany_id=campany_id)
    if is_ok:
        #
        data["eanTypeCount"] = len(data["eanInfo"])
        eanCount = 0
        hasUpload = 0
        uploadError = 0
        unUpload = 0
        for ean_info in data["eanInfo"]:
            eanCount += ean_info.get("count", 0)
            uploadStatus = ean_info.get("uploadStatus", 0)
            if uploadStatus == 0:
                unUpload += 1
            elif uploadStatus == 1:
                hasUpload += 1
            elif uploadStatus == 2:
                uploadError += 1
            is_ok, ean_data = await get_packing_data_by_ean(ean_info["ean"], campany_id)
            if type(ean_data) == dict:
                ean_info["images"] = ean_data["images"]
                ean_info["listingName"] = ean_data["listingName"]
                ean_info["id"] = ean_data["id"]
                ean_info["length"] = ean_data["length"]
                ean_info["width"] = ean_data["width"]
                ean_info["height"] = ean_data["height"]
                ean_info["weight"] = ean_data["weight"]
        data["eanCount"] = eanCount
        data["hasUpload"] = hasUpload
        data["uploadError"] = uploadError
        data["unUpload"] = unUpload

        return json(**SuccessResponse(message="OK", data=data).to_response())
    else:
        return json(**FailureResponse(message=data, data={}).to_response())


@bp_em_reception.post("/formUploadExcel")
@protected(permission=["emReceptionManager:list"], needVip=True)
async def em_reception_form_upload_excel(request: Request):
    """
    更新店铺
    :param request:
    :return:
    """
    campany_id = await get_user_campany_id_by_request(request)
    emReceptionId = request.json.get("emReceptionId", None)
    receptionId = request.json.get("receptionId", None)
    company_info = request.json.get("company_info", None)
    rep = request.json.get("rep", None)
    eanInfo = request.json.get("eanInfo", None)
    if not emReceptionId:
        return json(**FailureResponse(message="未找到面单", data={}).to_response())
    return await form_em_reception_excel(emReceptionId, receptionId, company_info, rep, eanInfo, campany_id=campany_id)


@bp_em_reception.post("/changeEanUploadStatus")
@protected(permission=["emReceptionManager:update"], needVip=True)
async def em_reception_change_ean_upload_status(request: Request):
    """
    更新店铺
    :param request:
    :return:
    """
    campany_id = await get_user_campany_id_by_request(request)
    emReceptionId = request.json.get("emReceptionId", None)
    uploadStatus = request.json.get("uploadStatus", 0)
    eans = request.json.get("ean", None)
    is_ok, msg = await change_ean_status(emReceptionId, campany_id, eans, uploadStatus)
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_em_reception.post("/createShipmentsOrder")
@protected(permission=["emReceptionManager:update"], needVip=True)
async def em_reception_create_shipments_order(request: Request):
    """
    更新店铺
    :param request:
    :return:
    """
    campany_id = await get_user_campany_id_by_request(request)
    emReceptionId = request.json.get("emReceptionId", None)
    domesticLogistics = request.json.get("domesticLogistics", None)
    internationalLogistics = request.json.get("internationalLogistics", 0)
    sendToWhId = request.json.get("sendToWhId", None)
    is_ok, msg = await create_shipments_order(emReceptionId, campany_id, domesticLogistics, internationalLogistics,
                                              sendToWhId)
    if is_ok:
        return json(**SuccessResponse(message=msg, data={"shipmentsOrderId":msg}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())
