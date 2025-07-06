# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：packing_box_info.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-04-17 15:30 
-------------------------------------
'''
import time

from loguru import logger
from sanic import Blueprint, json, Request

from apps.packing_box_info.tool import get_packing_box_info, add_box_in_packing_info, check_packing_info_version, \
    delete_box_in_packing_info, add_ean_in_packing_info, init_packing_summary_ean_info, remove_ean_packing_info, \
    create_em_reception_task, create_yf_template
from apps.user.tool import get_user_campany_id_by_request
from config.bean import SuccessResponse, FailureResponse
from models.packing_box_info import PackingBoxInfo
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update
from utils.auth import protected
from utils.common import get_uuid, get_packing_order_id, args_valid
from utils.mongo_tool import add_filter_in_filters

bp_packing_box_info = Blueprint("packingBoxInfo", url_prefix="packingBoxInfo")  # 创建蓝图


@bp_packing_box_info.post("/list")
@protected(permission=["packingBoxInfoManager:list"], needVip=True)
async def packing_box_info_list(request: Request):
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
    data = await mongodb_list(collection_name=PackingBoxInfo.collection_name, fields=fields, filters=filters,
                              sorts=sorts,
                              current_page=current_page, page_size=page_size,seleted_shop=seleted_shop)
    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_packing_box_info.post("/create")
@protected(permission=["packingBoxInfoManager:create"], needVip=True)
async def packing_box_info_create(request: Request):
    """
    :param request:
    :return:
    """
    data: dict = request.json
    campany_id = await get_user_campany_id_by_request(request)
    data["campanyId"] = campany_id
    data["packingOrderId"] = get_packing_order_id()
    # 添加额外属性
    data["version"] = time.time()
    data["emReceptionId"] = None
    data["packingInfo"] = []
    data["packingSummary"] = {"eanToInfo": {}, "receptionId": None}
    # data["receptionId"] = None  # 转面单的面单ID
    #
    is_ok, msg = await mongodb_create(collection_name=PackingBoxInfo.collection_name, data=data,
                                      uni_field=["packingOrderId", "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_packing_box_info.post("/get")
@protected(permission=["packingBoxInfoManager:list"], needVip=True)
async def packing_box_info_get(request: Request):
    """
    :param request:
    :return:
    """
    data: dict = request.json
    packing_order_id = data.get("packingOrderId", None)
    if not packing_order_id:
        return json(**FailureResponse(message="装箱单ID不能为空!", data={}).to_response())
    campany_id = await get_user_campany_id_by_request(request)
    data = await get_packing_box_info(packing_order_id, campany_id)
    data["packingSummary"]["eanToInfo"] = await init_packing_summary_ean_info(data.get("packingInfo"), campany_id)
    for k in ["createTime", "updateTime"]:
        if k in data:
            data[k] = data[k].timestamp()
    if data:
        return json(**SuccessResponse(message="OK", data=data).to_response())
    else:
        return json(**FailureResponse(message="装箱单不存在", data={}).to_response())


@bp_packing_box_info.post("/update")
@protected(permission=["packingBoxInfoManager:update"], needVip=True)
async def packing_box_info_update(request: Request):
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
    is_ok, msg = await mongodb_update(collection_name=PackingBoxInfo.collection_name, data=update_data,
                                      uni_field=[id_field, "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_packing_box_info.post("/addBox")
@protected(permission=["packingBoxInfoManager:update"], needVip=True)
async def packing_box_info_add_box(request: Request):
    """
    :param request:
    :return:
    """
    data: dict = request.json
    version = data.get("version", None)
    campany_id = await get_user_campany_id_by_request(request)
    packingOrderId = data.get("packingOrderId", None)
    is_ok, msg, need_reload = await check_packing_info_version(packing_order_id=packingOrderId, campany_id=campany_id,
                                                               version=version)
    if not is_ok:
        return json(**SuccessResponse(message=msg, data={"need_reload": need_reload}).to_response())

    boxData = data.get("boxData", {}).get("data", {})
    new_box_item = {
        "boxInfo": {k: boxData.get(k, None) for k in ["boxId", "boxName", "boxL", "boxW", "boxH", "boxWeight"]},
        "mskuInBox": {}}
    is_ok = await add_box_in_packing_info(packing_order_id=packingOrderId, campany_id=campany_id,
                                          new_box_item=new_box_item)
    if is_ok:
        return json(**SuccessResponse(message="OK", data={"data": new_box_item}).to_response())
    else:
        return json(**FailureResponse(message="添加失败", data={}).to_response())


@bp_packing_box_info.post("/deleteBox")
@protected(permission=["packingBoxInfoManager:update"], needVip=True)
async def packing_box_info_delete_box(request: Request):
    """
    :param request:
    :return:
    """
    data: dict = request.json
    version = data.get("version", None)
    campany_id = await get_user_campany_id_by_request(request)
    packingOrderId = data.get("packingOrderId", None)
    is_ok, msg, need_reload = await check_packing_info_version(packing_order_id=packingOrderId, campany_id=campany_id,
                                                               version=version)
    if not is_ok:
        return json(**SuccessResponse(message=msg, data={"need_reload": need_reload}).to_response())

    boxIndex = data.get("boxIndex", {})
    is_ok = await delete_box_in_packing_info(packing_order_id=packingOrderId, campany_id=campany_id,
                                             box_index=boxIndex)
    if is_ok:
        return json(**SuccessResponse(message="OK", data={}).to_response())
    else:
        return json(**FailureResponse(message="删除失败", data={}).to_response())


@bp_packing_box_info.post("/addEanToBox")
@protected(permission=["packingBoxInfoManager:update"], needVip=True)
async def packing_box_info_add_ean_to_box(request: Request):
    """
    :param request:
    :return:
    """
    data: dict = request.json
    version = data.get("version", None)
    campany_id = await get_user_campany_id_by_request(request)
    packingOrderId = data.get("packingOrderId", None)
    is_ok, msg, need_reload = await check_packing_info_version(packing_order_id=packingOrderId, campany_id=campany_id,
                                                               version=version)
    if not is_ok:
        return json(**SuccessResponse(message=msg, data={"need_reload": need_reload}).to_response())
    boxIndex = data.get("boxIndex", None)
    ean = data.get("ean", None)
    count = data.get("count", 1)
    whId = data.get("whId", None)
    if not args_valid([campany_id, boxIndex, ean, count]):
        return json(**FailureResponse(message="添加失败", data={}).to_response())
    is_ok,msg = await add_ean_in_packing_info(packing_order_id=packingOrderId, campany_id=campany_id,
                                          box_index=boxIndex, ean=ean, count=count,whId=whId)
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_packing_box_info.post("/removeEanFromBox")
@protected(permission=["packingBoxInfoManager:update"], needVip=True)
async def packing_box_info_remove_ean_from_box(request: Request):
    """
    :param request:
    :return:
    """
    data: dict = request.json
    version = data.get("version", None)
    campany_id = await get_user_campany_id_by_request(request)
    packingOrderId = data.get("packingOrderId", None)
    is_ok, msg, need_reload = await check_packing_info_version(packing_order_id=packingOrderId, campany_id=campany_id,
                                                               version=version)
    if not is_ok:
        return json(**SuccessResponse(message=msg, data={"need_reload": need_reload}).to_response())
    boxIndex = data.get("boxIndex", None)
    ean = data.get("ean", None)
    count = data.get("count", 1)
    whId = data.get("whId", None)
    if not args_valid([campany_id, boxIndex, ean, count]):
        return json(**FailureResponse(message="出箱失败", data={}).to_response())
    is_ok,msg = await remove_ean_packing_info(packing_order_id=packingOrderId, campany_id=campany_id,
                                          box_index=boxIndex, ean=ean, count=count,whId=whId)
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_packing_box_info.post("/uploadEmReception")
@protected(permission=["emReceptionManager:create"], needVip=True)
async def packing_box_info_upload_em_reception(request: Request):
    """
    :param request:
    :return:
    """
    data: dict = request.json
    version = data.get("version", None)
    campany_id = await get_user_campany_id_by_request(request)
    packingOrderId = data.get("packingOrderId", None)
    is_ok, msg, need_reload = await check_packing_info_version(packing_order_id=packingOrderId, campany_id=campany_id,
                                                               version=version)
    if not is_ok:
        return json(**SuccessResponse(message=msg, data={"need_reload": need_reload}).to_response())
    is_ok,msg = await create_em_reception_task(packing_order_id=packingOrderId, campany_id=campany_id)
    if is_ok:
        return json(**SuccessResponse(message="OK", data=msg).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_packing_box_info.post("/formYfTemplate")
@protected(permission=["emReceptionManager:list"], needVip=True)
async def packing_box_info_form_yf_template(request: Request):
    """
    :param request:
    :return:
    """
    data: dict = request.json
    version = data.get("version", None)
    campany_id = await get_user_campany_id_by_request(request)
    packingOrderId = data.get("packingOrderId", None)
    logisticProvidor = data.get("logisticProvidor", None)
    is_ok, msg, need_reload = await check_packing_info_version(packing_order_id=packingOrderId, campany_id=campany_id,
                                                               version=version)
    if not is_ok:
        return json(**SuccessResponse(message=msg, data={"need_reload": need_reload}).to_response())
    return await create_yf_template(packing_order_id=packingOrderId, campany_id=campany_id,logistic_providor=logisticProvidor)


