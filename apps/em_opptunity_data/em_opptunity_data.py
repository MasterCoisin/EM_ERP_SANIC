# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：em_opptunity_data.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-04-03 22:49 
-------------------------------------
'''
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorCollection
from sanic import Blueprint, json, Request

from apps.em_opptunity_data.tool import get_opp_data_version
from apps.user.tool import get_user_campany_id_by_request
from config.bean import SuccessResponse, FailureResponse
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update
from utils.auth import protected
from utils.mongo_tool import add_filter_in_filters

bp_em_opptunity_data = Blueprint("emOpptunityData", url_prefix="emOpptunityData")  # 创建蓝图


@bp_em_opptunity_data.post("/list")
@protected(permission=[],needVip=True)
async def em_opptunity_data_list(request: Request):
    """
    :param request:
    :return:
    """
    current_page, page_size, fields, filters, sorts = get_request_base_params(request)
    campany_id = await get_user_campany_id_by_request(request)
    version = request.json.get("version",None)
    versions = await get_opp_data_version()
    if not version:
        version = versions[0]
    data = await mongodb_list(collection_name=f"opp_category_week_index_{version}",
                              fields=["key", 'SuperHotRate', "title", "highRiskCategory", "advertisingNotAllowed",
                                      "totalCount", "hasSoldCount", 'superHotCount', 'hasSoldRate', 'hotCount',
                                      'standardCount','nameRo'], filters=filters, sorts=sorts,
                              current_page=current_page, page_size=page_size, is_opp_db=True)
    keys = [i.get("key", None) for i in data["data"]]
    #
    collection: AsyncIOMotorCollection = request.app.ctx.mongo_em_data["opp_category"]
    result = await collection.find({"key": {"$in": keys}}, {"key": 1, "cateUrl": 1}).to_list()
    result = {i["key"]: i for i in result}
    #
    collection2: AsyncIOMotorCollection = request.app.ctx.mongo_em_data["collection"]
    result2 = await collection2.find({"key": {"$in": keys}, "campanyId": campany_id}, {"key": 1}).to_list()
    result2 = {i["key"]: i for i in result2}
    for i in data["data"]:
        i["cateUrl"] = result.get(i["key"], {}).get("cateUrl", None)
        i["isFavorite"] = i["key"] in result2
    return json(**SuccessResponse(message="OK", data={"data":data,"version":version,"versions":[{"value":i,"label":str(i)} for i in versions]}).to_response())


@bp_em_opptunity_data.post("/collection")
@protected(permission=[],needVip=True)
async def em_opptunity_data_collection(request: Request):
    """
    :param request:
    :return:
    """
    key = request.json.get("key", None)
    isFavorite = request.json.get("isFavorite", False)
    campany_id = await get_user_campany_id_by_request(request)
    collection: AsyncIOMotorCollection = request.app.ctx.mongo_em_data["collection"]
    if isFavorite:
        result = await collection.update_one({"key": key, "campanyId": campany_id},
                                             {"$set": {"key": key, "campanyId": campany_id}}, upsert=True)
    else:
        result = await collection.find_one_and_delete({"key": key, "campanyId": campany_id})
    return json(**SuccessResponse(message="OK", data={}).to_response())


@bp_em_opptunity_data.post("/listFavorite")
@protected(permission=[],needVip=True)
async def em_opptunity_data_list_favorite(request: Request):
    """
    :param request:
    :return:
    """
    current_page, page_size, fields, filters, sorts = get_request_base_params(request)
    campany_id = await get_user_campany_id_by_request(request)
    filters = add_filter_in_filters(filters, "campanyId", campany_id)
    data = await mongodb_list(collection_name="collection",
                              fields=["key"], filters=filters, sorts=sorts,
                              current_page=current_page, page_size=page_size, is_opp_db=True)
    keys = [i.get("key", None) for i in data["data"]]
    #
    collection: AsyncIOMotorCollection = request.app.ctx.mongo_em_data["opp_category"]
    result = await collection.find({"key": {"$in": keys}}, {"key": 1, "cateUrl": 1}).to_list()
    result = {i["key"]: i for i in result}
    #
    versions = await get_opp_data_version()
    collection2: AsyncIOMotorCollection = request.app.ctx.mongo_em_data[f"opp_category_week_index_{versions[0]}"]
    result2 = await collection2.find({"key": {"$in": keys}},
                                     {"key": 1, "SuperHotRate": 1, "title": 1, "highRiskCategory": 1,
                                      "advertisingNotAllowed": 1, "totalCount": 1, "hasSoldCount": 1,
                                      "superHotCount": 1, "hasSoldRate": 1, "hotCount": 1,
                                      "standardCount": 1,"_id":0,"nameRo":1}).to_list()
    for i in result2:
        i["cateUrl"] = result.get(i["key"], {}).get("cateUrl", None)
        i["isFavorite"] = True
    data["data"] = result2
    return json(**SuccessResponse(message="OK", data=data).to_response())

