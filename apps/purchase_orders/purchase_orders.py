# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：purchase_orders.py
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

from apps.purchase_orders.tools import get_1688_address, init_all_shop_address, get_today_in_purchase_sku_info
from apps.user.tool import get_user_campany_id_by_request
from config.bean import SuccessResponse, FailureResponse
from models.purchase_orders import PurchaseOrders
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update
from utils.auth import protected
from utils.common import args_valid
from utils.mongo_tool import add_filter_in_filters

bp_purchase_orders = Blueprint("purchaseOrders", url_prefix="purchaseOrders")  # 创建蓝图


@bp_purchase_orders.post("/list")
@protected(permission=["purchaseOrders:list"],needVip=True)
async def purchase_orders_list(request: Request):
    """
    查询采购单列表
    :param request:
    :return:
    """
    current_page, page_size, fields, filters, sorts = get_request_base_params(request)
    campany_id = await get_user_campany_id_by_request(request)
    if "createTime" not in [i["field"] for i in sorts]:
        sorts.append({"field": "createTime", "t": "desc"})
    filters = add_filter_in_filters(filters, "campanyId", campany_id)
    data = await mongodb_list(collection_name=PurchaseOrders.collection_name, fields=fields, filters=filters,
                              sorts=sorts,
                              current_page=current_page, page_size=page_size)
    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_purchase_orders.post("/get_skus")
@protected(permission=["purchaseOrders:list"],needVip=True)
async def purchase_orders_get_skus(request: Request):
    """
    查询采购单skus
    :param request:
    :return:
    """
    purchase_order_id = request.json.get("purchaseOrderId", [])
    filters = [{"field": "purchaseOrderId", "query": str(purchase_order_id), "t": "regex"}]
    campany_id = await get_user_campany_id_by_request(request)
    filters = add_filter_in_filters(filters, "campanyId", campany_id)
    data = await mongodb_list(collection_name=PurchaseOrders.collection_name, fields=[],
                              filters=filters,
                              sorts=[],
                              current_page=1, page_size=1)
    if data["data"]:
        skus_list = [i["skus"] for i in data["data"][0].get("orders", {}).values()]
    else:
        skus_list = []
    res = []
    for skus in skus_list:
        res += skus
    footer_data = {"seq": '合计', "count": 0, "inboundCount": 0}
    if res:
        footer_data["count"] = sum([i.get("count", 0) if i.get("count", 0) else 0 for i in res])
        footer_data["inboundCount"] = sum([i.get("inboundCount", 0) if i.get("inboundCount", 0) else 0 for i in res])
    return json(**SuccessResponse(message="OK", data={"skus": res, "footerData": [footer_data]}).to_response())


@bp_purchase_orders.post("/get_sku_info")
@protected(permission=["purchaseOrders:list"],needVip=True)
async def purchase_orders_get_sku_info(request: Request):
    """
    查询采购单skus
    :param request:
    :return:
    """
    purchase_order_id = request.json.get("purchaseOrderId", [])
    filters = [{"field": "purchaseOrderId", "query": None, "t": "eq", "value": str(purchase_order_id)}]
    campany_id = await get_user_campany_id_by_request(request)
    filters = add_filter_in_filters(filters, "campanyId", campany_id)

    await PurchaseOrders.check_status_and_update(purchase_order_id, campany_id)

    data = await mongodb_list(collection_name=PurchaseOrders.collection_name, fields=[],
                              filters=filters,
                              sorts=[],
                              current_page=1, page_size=1)
    if data["data"]:
        data = data["data"][0]
        orders = {}
        for s_id in data["orders"].keys():
            if data["orders"][s_id]["deleted"]!=True:
                orders[s_id] = data["orders"][s_id]
        data["orders"] = orders
        return json(**SuccessResponse(message="OK", data=data).to_response())
    return json(**FailureResponse(message="未找到采购单").to_response())


@bp_purchase_orders.post("/create")
@protected(permission=["purchaseOrders:create"],needVip=True)
async def purchase_orders_create(request: Request):
    """
    创建采购单
    :param request:
    :return:
    """
    sku_infos = request.json.get('sku_infos', None)
    if not args_valid([sku_infos]):
        return json(**FailureResponse(message="参数不完整", data={}).to_response())
    if type(sku_infos) == list:
        data = {}
        for sku in sku_infos:
            data[sku["sku"]] = data.get(sku["sku"], 0) + sku["count"]
        data = [{"sku": k, "count": v} for k, v in data.items()]
    elif type(sku_infos) == dict:
        data = [{"sku": k, "count": v} for k, v in sku_infos.items()]
    else:
        return json(**FailureResponse(message="error", data={}).to_response())
    campany_id = await get_user_campany_id_by_request(request)
    is_ok, msg, purchase_order_id = await PurchaseOrders.create_purchase_order(skus=data, campany_id=campany_id)
    if is_ok:
        return json(**SuccessResponse(message=msg, data={"purchase_order_id": purchase_order_id}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_purchase_orders.post("/update")
@protected(permission=["purchaseOrders:update"],needVip=True)
async def purchase_orders_update(request: Request):
    """
    更新采购单
    :param request:
    :return:
    """
    data: dict = request.json
    _id = data.get("id", None)
    id_field = data.get("id_field", "open_id")
    update_data = data.get("data", {})
    update_data[id_field] = _id
    campany_id = await get_user_campany_id_by_request(request)
    update_data["campanyId"] = campany_id
    is_ok, msg = await mongodb_update(collection_name=PurchaseOrders.collection_name, data=update_data,
                                      uni_field=[id_field, "campanyId"])
    await PurchaseOrders.check_status_and_update(update_data[id_field], campany_id)
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_purchase_orders.post("/delete")
@protected(permission=["purchaseOrders:delete"],needVip=True)
async def purchase_orders_delete(request: Request):
    purchase_order_id = request.json.get('purchaseOrderId', None)
    supplier_uuid = request.json.get('supplierUuid', None)
    campany_id = await get_user_campany_id_by_request(request)
    if purchase_order_id is not None:
        if not supplier_uuid:
            if await PurchaseOrders.delete(purchase_order_id, campany_id):
                await PurchaseOrders.check_status_and_update(purchase_order_id, campany_id)
                return json(**SuccessResponse(message="删除采购单成功", data={}).to_response())
        else:
            if await PurchaseOrders.delete_supplier(purchase_order_id, supplier_uuid, campany_id):
                await PurchaseOrders.check_status_and_update(purchase_order_id, campany_id)
                return json(**SuccessResponse(message="删除供应商订单成功", data={}).to_response())

    return json(**FailureResponse(message="删除失败", data={}).to_response())


@bp_purchase_orders.post("/changeStatusFapiao")
@protected(permission=["purchaseOrders:update"],needVip=True)
async def purchase_orders_change_status_fapiao(request: Request):
    """
    更新开票状态
    :param request:
    :return:
    """
    purchase_order_id = request.json.get('purchaseOrderId', None)
    supplier_uuid = request.json.get('supplierUuid', None)
    has_fapiao = request.json.get('has_fapiao', None)
    has_kaipiao = request.json.get('has_kaipiao', None)
    has_print_fapiao = request.json.get('has_print_fapiao', None)
    campany_id = await get_user_campany_id_by_request(request)
    if purchase_order_id is not None:
        if await PurchaseOrders.change_status_fapiao(purchase_order_id, supplier_uuid, has_fapiao, has_kaipiao,
                                                     has_print_fapiao, campany_id):
            return json(**SuccessResponse(message="更新成功", data={}).to_response())
    return json(**FailureResponse(message="", data={}).to_response())


@bp_purchase_orders.get("/get1688Address")
@protected(needVip=True)
async def purchase_orders_get_1688_address(request: Request):
    campany_id = await get_user_campany_id_by_request(request)
    return json(**SuccessResponse(message="OK", data=await get_1688_address(campany_id=campany_id)).to_response())


@bp_purchase_orders.get("/init1688Address")
@protected(needVip=True)
async def purchase_orders_init_1688_address(request: Request):
    await init_all_shop_address()
    return json(**SuccessResponse(message="OK", data={}).to_response())


@bp_purchase_orders.post("/createOrderAuto")
@protected(permission=["purchaseOrder:create"],needVip=True)
async def purchase_orders_create_order_auto(request: Request):
    """
    1688下单
    :param request:
    :return:
    """
    supplier_uuid = request.json.get('supplierUuid', None)
    address_id = request.json.get('addressId', None)
    tip_for_seller = request.json.get('tip_for_seller', None)
    purchase_order_id = request.json.get('purchaseOrderId', None)
    shop_id = request.json.get('shopId', "wl")
    campany_id = await get_user_campany_id_by_request(request)
    if not args_valid([supplier_uuid, address_id, tip_for_seller, purchase_order_id, shop_id]):
        return json(**FailureResponse(message="参数不完整", data={}).to_response())
    is_ok, msg = await PurchaseOrders.create_order_auto(supplier_uuid, address_id, tip_for_seller, purchase_order_id,
                                                        shop_id, campany_id)
    await PurchaseOrders.check_status_and_update(purchase_order_id, campany_id)
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_purchase_orders.post("/createOrderNot1688")
@protected(permission=["purchaseOrders:create"],needVip=True)
async def purchase_orders_create_order_not_1688(request: Request):
    """
    非1688下单
    :param request:
    :return:
    """
    supplier_uuid = request.json.get('supplierUuid', None)
    purchase_order_id = request.json.get('purchaseOrderId', None)
    skus = request.json.get('skus', {})
    shop_id = request.json.get('shopId', "wl")
    campany_id = await get_user_campany_id_by_request(request)
    if not args_valid([supplier_uuid, skus, purchase_order_id, shop_id]):
        return json(**FailureResponse(message="参数不完整", data={}).to_response())

    is_ok, msg = await PurchaseOrders.create_order_not_1688(supplier_uuid, purchase_order_id, skus, shop_id, campany_id)
    await PurchaseOrders.check_status_and_update(purchase_order_id, campany_id)
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_purchase_orders.post("/changeStatusNot1688")
@protected(permission=["purchaseOrders:update"],needVip=True)
async def purchase_orders_change_status_not_1688(request: Request):
    supplier_uuid = request.json.get('supplierUuid', None)
    purchase_order_id = request.json.get('purchaseOrderId', None)
    status = request.json.get('status', None)
    shop_id = request.json.get('shopId', "wl")
    campany_id = await get_user_campany_id_by_request(request)
    print(supplier_uuid, purchase_order_id, status, shop_id)
    if not args_valid([supplier_uuid, purchase_order_id, status, shop_id]):
        return json(**FailureResponse(message="参数不完整", data={}).to_response())
    is_ok, msg = await PurchaseOrders.change_status_not_1688(supplier_uuid, purchase_order_id, shop_id, campany_id,
                                                             status)
    await PurchaseOrders.check_status_and_update(purchase_order_id, campany_id)
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_purchase_orders.post("/inbound")
@protected(permission=["purchaseOrders:update"],needVip=True)
async def purchase_orders_inbound(request: Request):
    supplier_uuid = request.json.get('supplierUuid', None)
    purchase_order_id = request.json.get('purchaseOrderId', None)
    skus = request.json.get('skus', [])
    campany_id = await get_user_campany_id_by_request(request)
    if not args_valid([supplier_uuid, purchase_order_id, skus]):
        return json(**FailureResponse(message="参数不完整", data={}).to_response())
    is_ok, msg = await PurchaseOrders.inbound(supplier_uuid, purchase_order_id, skus, campany_id)
    await PurchaseOrders.check_status_and_update(purchase_order_id, campany_id)
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_purchase_orders.post("/changeInboundInfo")
@protected(permission=["purchaseOrders:update"],needVip=True)
async def purchase_orders_change_inbound_info(request: Request):
    supplier_uuid = request.json.get('supplierUuid', None)
    purchase_order_id = request.json.get('purchaseOrderId', None)
    skus = request.json.get('skus', [])
    campany_id = await get_user_campany_id_by_request(request)
    if not args_valid([supplier_uuid, purchase_order_id, skus]):
        return json(**FailureResponse(message="参数不完整", data={}).to_response())
    is_ok, msg = await PurchaseOrders.change_inbound_info(supplier_uuid, purchase_order_id, skus, campany_id)
    await PurchaseOrders.check_status_and_update(purchase_order_id,campany_id)
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())

@bp_purchase_orders.post("/getTodayInPurchaseSku")
@protected(permission=["purchaseOrders:list"],needVip=True)
async def purchase_orders_get_today_in_purchase_sku(request: Request):
    """
    查询采购单列表
    :param request:
    :return:
    """
    campany_id = await get_user_campany_id_by_request(request)
    data = await get_today_in_purchase_sku_info(campany_id)
    return json(**SuccessResponse(message="OK", data=data).to_response())
