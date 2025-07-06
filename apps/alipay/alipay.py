# -*- coding: UTF-8 -*-
'''
@Project     ：em_buy_carts_monitor_backen 
@File        ：alipay.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-03-10 0:36 
-------------------------------------
'''
from sanic import Blueprint, json, Request, text
from loguru import logger

from apps.order.tool import pay_success

bp_alipayPro = Blueprint("alipayPro", url_prefix="alipayPro")  # 创建蓝图


@bp_alipayPro.post("/messageReciver")
async def messageReciver(request: Request):
    """
    :param request:
    :return:
    """
    try:
        data = request.form
        print(type(data))
        print(data)
        out_trade_no = data.get("out_trade_no", None)
        print(out_trade_no)
        await pay_success(out_trade_no)
        return text("success")
    except Exception as e:
        logger.exception(e)
