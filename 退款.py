# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：退款.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-04-10 15:01 
-------------------------------------
'''
from alipayApi.alipayTook import aliPayTool

aliPayTool.api_alipay_trade_refund("ON1744270596",0.03,"退款")

