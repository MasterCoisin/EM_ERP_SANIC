# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：listing.py
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

from apps.ean.tool import get_ean
from apps.images.tool import url_to_id
from apps.listing.tool import parse_to_list, get_packing_data_by_ean, save_expain_to_server, create_em_product_excel
from apps.msku_inventory_detail.tool import count_status_by_batch, count_sold_by_batch, get_ean_sold_per_day, \
    get_ean_sold_per_week, get_ean_sold_per_month, get_ean_sold_per_year
from apps.msku_inventory_index.tool import get_data_by_ean
from apps.product.tools import get_data_by_skus
from apps.user.tool import get_user_campany_id_by_request
from config.bean import SuccessResponse, FailureResponse
from models.listing import Listing
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update
from utils.auth import protected
from utils.common import price_deal
from utils.mongo_tool import add_filter_in_filters

bp_listing = Blueprint("listing", url_prefix="listing")  # 创建蓝图


@bp_listing.post("/list")
@protected(permission=["listingManager:list"], needVip=True)
async def listing_list(request: Request):
    """
    查询产品列表
    :param request:
    :return:
    """
    current_page, page_size, fields, filters, sorts = get_request_base_params(request)
    seleted_shop = request.json.get("seleted_shop", "wl")
    if "createTime" not in [i["field"] for i in sorts]:
        sorts.append({"field": "createTime", "t": "desc"})
    campany_id = await get_user_campany_id_by_request(request)
    filters = add_filter_in_filters(filters, "campanyId", campany_id)
    data = await mongodb_list(collection_name=Listing.collection_name, fields=fields, filters=filters, sorts=sorts,
                              current_page=current_page, page_size=page_size, seleted_shop=seleted_shop)
    # 合并ean库存信息
    eans = [i["ean"] for i in data["data"]]
    ean_data = await get_data_by_ean(eans)
    ean_data = {i["ean"]: {
        "mskuAvgFee": price_deal(i.get("mskuAvgFee", None)),
        "mskuFinallInboundDate": i.get("mskuFinallInboundDate", None),
        "mskuFirstInboundDate": i.get("mskuFirstInboundDate", None),
        "mskuHasDestroyed": i.get("mskuHasDestroyed", None),
        "mskuHasLosed": i.get("mskuHasLosed", None),
        "mskuHasPurchased": i.get("mskuHasPurchased", None),
        "mskuSendTimes": i.get("mskuSendTimes", None),
        "mskuTotalSent": i.get("mskuTotalSent", None),
        "mskuLeft": i.get("mskuLeft", None),
        "mskuInTrans": i.get("mskuInTrans", None),
        "mskuAvgBuyAndHeadFee": price_deal(i.get("mskuAvgBuyAndHeadFee", None)),
        "mskuAvgHeadFee": price_deal(i.get("mskuAvgHeadFee", None)),
    } for i in await ean_data}
    # 库存品批次情况
    count_status_by_batch_data = await count_status_by_batch(company_id=campany_id, eans=eans)
    # 销量
    count_sold_by_batch_data = await count_sold_by_batch(company_id=campany_id, eans=eans)
    # 合并sku信息

    skus = set()
    for row in data["data"]:
        for sku_info in row.get("skuList", []):
            skus.add(sku_info["sku"])
    skus_info_dict = await get_data_by_skus(list(skus), campany_id)
    for row in data["data"]:
        for idx, sku_info in enumerate(row.get("skuList", [])):
            row["skuList"][idx] = {**sku_info, **skus_info_dict.get(sku_info["sku"], {})}
        # 库存品批次情况
        row["countStatusByBatchData"] = count_status_by_batch_data.get(row.get("ean", None), [])
        # 销量
        row["soldCount"] = count_sold_by_batch_data.get(row.get("ean", None),
                                                        {'week': 0, 'month': 0, 'season': 0, 'year': 0})
    #
    data["data"] = [await parse_to_list(d, ean_data.get(d["ean"], {})) for d in data["data"]]

    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_listing.post("/create")
@protected(permission=["listingManager:create"], needVip=True)
async def listing_create(request: Request):
    """
    创建产品
    :param request:
    :return:
    """
    data: dict = request.json
    campany_id = await get_user_campany_id_by_request(request)
    data["campanyId"] = campany_id
    data["images"] = url_to_id(data.get("images", []))
    # 处理ean问题
    if not data.get("ean", None):
        ean = await get_ean(campany_id=campany_id)
        if ean:
            data["ean"] = ean
        else:
            return json(**FailureResponse(message="暂无可分配ean,请前往添加!", data={}).to_response())
    # 处理skuList和packingList
    for k in ["skuList", "packingList"]:
        data[k] = [{"sku": i["sku"], "count": i["count"]} for i in data[k]]
    is_ok, msg = await mongodb_create(collection_name=Listing.collection_name, data=data, uni_field=["ean"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_listing.post("/update")
@protected(permission=["listingManager:update"], needVip=True)
async def listing_update(request: Request):
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
    if "images" in update_data: update_data["images"] = url_to_id(update_data.get("images", []))
    for k in ["skuList", "packingList"]:
        if k in update_data:
            update_data[k] = [{"sku": i["sku"], "count": i["count"]} for i in update_data[k]]
    update_data = {k: v for k, v in update_data.items() if k in [
        "campanyId",
        "ean",
        "msku",
        "listingName",
        "listingNameEn",
        "images",
        "addFee",
        "invoiceInfo",
        "baseInfo",
        "emAttribute",
        "emSaleInfo",
        "flag",
        "gprs",
        "logisticsAttributes",
        "packingList",
        "skuList",
        "shop",
        "tip",
        "competitorUrls",
        "deleted",
        "createTime",
        "updateTime"
    ]}
    is_ok, msg = await mongodb_update(collection_name=Listing.collection_name, data=update_data, uni_field=[id_field])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_listing.post("/searchEan")
@protected(permission=["listingManager:list"], needVip=True)
async def listing_search_ean(request: Request):
    """
    更新产品
    :param request:
    :return:
    """
    data: dict = request.json
    ean = data.get("ean", None)
    campany_id = await get_user_campany_id_by_request(request)
    is_ok, data = await get_packing_data_by_ean(ean, campany_id)
    if is_ok:
        return json(**SuccessResponse(message="OK", data=data).to_response())
    else:
        return json(**FailureResponse(message=str(data), data={}).to_response())


@bp_listing.post("/saveExpainToServer")
@protected(permission=["listingManager:update"], needVip=True)
async def listing_save_expain_to_server(request: Request):
    """
    更新产品
    :param request:
    :return:
    """
    data: dict = request.json
    ean = data.get("ean", None)
    html = data.get("html", None)
    campany_id = await get_user_campany_id_by_request(request)
    is_ok = await save_expain_to_server(ean, html)
    if is_ok:
        return json(**SuccessResponse(message="OK", data={}).to_response())
    else:
        return json(**FailureResponse(message="保存失败", data={}).to_response())


@bp_listing.post("/createEmProductExcel")
@protected(permission=["listingManager:list"], needVip=True)
async def listing_create_em_product_excel(request: Request):
    """
    更新产品
    :param request:
    :return:
    """
    data: dict = request.json
    eans = data.get("eans", None)
    campany_id = await get_user_campany_id_by_request(request)
    return await create_em_product_excel(eans, campany_id)


@bp_listing.post("/getEanSoldTrency")
@protected(permission=["listingManager:list"], needVip=True)
async def listing_get_ean_sold_trency(request: Request):
    """
    :param request:
    :return:
    """
    data: dict = request.json
    ean = data.get("ean", None)
    period = data.get("period", "day")
    campany_id = await get_user_campany_id_by_request(request)
    if period == "day":
        x, y = await get_ean_sold_per_day(campany_id, ean)
    elif period == "week":
        x, y = await get_ean_sold_per_week(campany_id, ean)
    elif period == "month":
        x, y = await get_ean_sold_per_month(campany_id, ean)
    else:
        x, y = await get_ean_sold_per_year(campany_id, ean)
    return json(**SuccessResponse(message="OK", data={"x": x, "y": y}).to_response())
