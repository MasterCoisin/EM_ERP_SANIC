# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：shop.py
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

from apps.shop.tool import get_shop_em_hash
from baken_task.update_em_product_offer import updata_pnk_from_em
from config.bean import SuccessResponse, FailureResponse
from utils.auth import protected
from utils.common import get_hash

bp_tasks = Blueprint("tasks", url_prefix="tasks")  # 创建蓝图


@bp_tasks.post("/addUpdateProductOfferTask")
@protected(permission=["tasks:create"],needVip=True)
async def add_update_product_offer_task(request: Request):
    """
    :param request:
    :return:
    """
    country = request.json.get("country","ro")
    shop_id = request.json.get("shop_id","wl")
    shop_hash = await get_shop_em_hash(shop_id=shop_id)
    if shop_hash:
        request.app.ctx.queue.put_nowait(updata_pnk_from_em(country=country,shop_hash=shop_hash))
    return json(**SuccessResponse(message="OK", data={}).to_response())


