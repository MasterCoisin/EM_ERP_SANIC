# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：em_search_by_image.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-04-29 19:12 
-------------------------------------
'''
from loguru import logger
from sanic import Blueprint, json, Request

from apps.em_search_by_image.tool import get_em_search_result
from config.bean import SuccessResponse, FailureResponse
from models.shop import Shop
from utils.auth import protected
from utils.mongo_tool import add_filter_in_filters

bp_em_search_by_image = Blueprint("emSearchByImage", url_prefix="emSearchByImage")  # 创建蓝图


@bp_em_search_by_image.post("/search")
@protected(needVip=True)
async def em_search_by_image_search(request: Request):
    """
    :param request:
    :return:
    """
    image = request.json.get("image",None)
    data = await get_em_search_result(image=image)
    return json(**SuccessResponse(message="OK", data=data).to_response())
