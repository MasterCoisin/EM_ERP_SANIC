# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：product.py
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

from apps.images.tool import url_to_id, image_id_to_url
from apps.sku_inventory_index.tool import get_data_by_sku
from apps.sku_warehouse.tool import get_sku
from apps.user.tool import get_user_campany_id_by_request
from config.bean import SuccessResponse, FailureResponse
from models.product import Product
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update
from utils.auth import protected
from utils.mongo_tool import add_filter_in_filters

bp_product = Blueprint("product", url_prefix="product")  # 创建蓝图


@bp_product.post("/list")
@protected(permission=["productManager:list"], needVip=True)
async def product_list(request: Request):
    """
    查询产品列表
    :param request:
    :return:
    """
    current_page, page_size, fields, filters, sorts = get_request_base_params(request)
    if "createTime" not in [i["field"] for i in sorts]:
        sorts.append({"field": "createTime", "t": "desc"})
    campany_id = await get_user_campany_id_by_request(request)
    filters = add_filter_in_filters(filters, "campanyId", campany_id)
    data = await mongodb_list(collection_name=Product.collection_name, fields=fields, filters=filters, sorts=sorts,
                              current_page=current_page, page_size=page_size)
    # sku采购情况
    sku_data_dict = {}
    if data["data"]:
        sku_data = await get_data_by_sku([i["sku"] for i in data["data"]], campany_id)
        for document in await sku_data:
            # {'sku': '05pq', 'whId': '41b15e00-1d82-11ef-b71f-3938ce80ebf6', 'skuAvgFee': 111.65, 'skuBuyTimes': 1, 'skuLeft': 10, 'skuTotalBuy': 10, 'skuHasSend': 0}
            if document["sku"] not in sku_data_dict:
                sku_data_dict[document["sku"]] = {'skuAvgFee': document.get("skuAvgFee", 0),
                                                  'skuBuyTimes': document.get("skuBuyTimes", 0),
                                                  'skuLeft': document.get("skuLeft", 0),
                                                  'skuTotalBuy': document.get("skuTotalBuy", 0),
                                                  'skuHasSend': document.get("skuHasSend", 0)}
            else:
                sku_data_dict[document["sku"]]['skuBuyTimes'] += document.get("skuBuyTimes", 0)
                sku_data_dict[document["sku"]]['skuLeft'] += document.get("skuLeft", 0)
                sku_data_dict[document["sku"]]['skuHasSend'] += document.get("skuHasSend", 0)
                sku_data_dict[document["sku"]]['skuAvgFee'] = (
                                                                      sku_data_dict[document["sku"]]['skuAvgFee'] *
                                                                      sku_data_dict[document["sku"]][
                                                                          'skuTotalBuy'] + document.get("skuTotalBuy",
                                                                                                        0) * document.get(
                                                                  "skuAvgFee", 0)) / (sku_data_dict[document["sku"]][
                                                                                          'skuTotalBuy'] + document.get(
                    "skuTotalBuy", 0)) if (
                        sku_data_dict[document["sku"]]['skuTotalBuy'] + document.get("skuTotalBuy", 0) > 0) else 0
                sku_data_dict[document["sku"]]['skuTotalBuy'] += document.get("skuTotalBuy", 0)
    for s_d in data["data"]:
        s_d["purchaseInfo"] = sku_data_dict.get(s_d["sku"], {'skuAvgFee': None,
                                                             'skuBuyTimes': None,
                                                             'skuLeft': None,
                                                             'skuTotalBuy': None,
                                                             'skuHasSend': None})
        s_d["images"] = [image_id_to_url(i) for i in s_d.get("images", [])]
    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_product.post("/create")
@protected(permission=["productManager:create"], needVip=True)
async def product_create(request: Request):
    """
    创建产品
    :param request:
    :return:
    """
    data: dict = request.json
    campany_id = await get_user_campany_id_by_request(request)
    data["campanyId"] = campany_id
    data["images"] = url_to_id(data.get("images", []))
    if not data.get("sku", None):
        data["sku"] = await get_sku()
    is_ok, msg = await mongodb_create(collection_name=Product.collection_name, data=data,
                                      uni_field=["sku", "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_product.post("/update")
@protected(permission=["productManager:update"], needVip=True)
async def product_update(request: Request):
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
    update_data = {k: v for k, v in update_data.items() if
                   k in ["campanyId", "sku", "productName", "url1688", "images", "tip", "competitorUrls", "length",
                         "width", "height", "weight", "volumeWeight", "weighing", "supplierInfo", "createTime",
                         "updateTime", "isConsumables", "deleted"]}
    if "images" in update_data: update_data["images"] = url_to_id(update_data.get("images", []))
    is_ok, msg = await mongodb_update(collection_name=Product.collection_name, data=update_data,
                                      uni_field=[id_field, "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())
