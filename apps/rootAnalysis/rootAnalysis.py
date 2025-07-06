# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：rootAnalysis.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-07-02 22:40 
-------------------------------------
'''
from loguru import logger
from sanic import Blueprint, json, Request

from apps.rootAnalysis.tool import get_root_analysis_by_uuid
from apps.user.tool import get_user_campany_id, get_user_campany_id_by_request
from config.bean import SuccessResponse, FailureResponse
from models.root_analysis import rootAnalysis
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update
from utils.auth import protected
from utils.common import get_uuid
from utils.mongo_tool import add_filter_in_filters

from nltk import FreqDist
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

bp_root_analysis = Blueprint("rootAnalysis", url_prefix="rootAnalysis")  # 创建蓝图


@bp_root_analysis.post("/list")
@protected(permission=["rootAnalysis:list"])
async def root_analysislist(request: Request):
    """
    查询路由列表
    :param request:
    :return:
    """
    current_page, page_size, fields, filters, sorts = get_request_base_params(request)
    campany_id = await get_user_campany_id_by_request(request)
    filters = add_filter_in_filters(filters, "campanyId", campany_id)
    data = await mongodb_list(collection_name=rootAnalysis.collection_name, fields=fields, filters=filters, sorts=sorts,
                              current_page=current_page, page_size=page_size)
    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_root_analysis.post("/create")
@protected(permission=["rootAnalysis:create"])
async def root_analysiscreate(request: Request):
    """
    :param request:
    :return:
    """
    data: dict = request.json
    campany_id = await get_user_campany_id_by_request(request)
    data["campanyId"] = campany_id
    data["uuid"] = get_uuid()
    is_ok, msg = await mongodb_create(collection_name=rootAnalysis.collection_name, data=data,
                                      uni_field=["uuid", "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_root_analysis.post("/update")
@protected(permission=["rootAnalysis:update"])
async def root_analysisupdate(request: Request):
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
    is_ok, msg = await mongodb_update(collection_name=rootAnalysis.collection_name, data=update_data,
                                      uni_field=[id_field, "campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_root_analysis.post("/get")
@protected(permission=["rootAnalysis:list"], needVip=True)
async def root_analysis_get(request: Request):
    """
    :param request:
    :return:
    """
    campany_id = await get_user_campany_id_by_request(request)
    uuid = request.json.get("uuid", None)
    if not uuid:
        return json(**FailureResponse(message="未找到", data={}).to_response())
    data = await get_root_analysis_by_uuid(uuid=uuid,campany_id=campany_id)
    if data:
        return json(**SuccessResponse(message="OK", data=data).to_response())
    else:
        return json(**FailureResponse(message=data, data={}).to_response())


def get_divide_words(english_sentence):
    english_tokens = word_tokenize(english_sentence)
    # 移除停用词
    english_stopwords = set(stopwords.words('english'))
    filtered_tokens = [word for word in english_tokens if word.lower() not in english_stopwords]
    interpunctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%']  # 定义标点符号列表
    filtered_tokens = [word for word in filtered_tokens if word not in interpunctuations]  # 去除标点符号
    # 计算词频分布
    freq_dist = FreqDist(filtered_tokens)
    return list(freq_dist.items())


@bp_root_analysis.post("/devideWords")
@protected(permission=["rootAnalysis:update"])
async def root_analysis_devide_words(request: Request):
    data: dict = request.json
    usTexts = data.get("usTexts", [])
    otherTexts = data.get("otherTexts", [])
    useUsTexts = data.get("useUsTexts", False)
    words_frequency = {}
    if useUsTexts:
        for i in usTexts:
            for item in get_divide_words(i["text"]):
                words_frequency[item[0]] = words_frequency.get(item[0], 0) + item[1]
    for i in otherTexts:
        for item in get_divide_words(i["text"]):
            words_frequency[item[0]] = words_frequency.get(item[0], 0) + item[1]
    words_frequency = [{"word": k, "count": v, "select": True} for k, v in words_frequency.items()]
    words_frequency = sorted(words_frequency, key=lambda x: -x["count"])
    return json(**SuccessResponse(message="OK", data=words_frequency).to_response())
