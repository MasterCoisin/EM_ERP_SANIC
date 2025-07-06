# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：genius_fee_cal.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-03-17 22:01 
-------------------------------------
'''
from config.constant import RON_TO_RMB, BGN_TO_RMB, VAT, HUF_TO_RMB


def genius_fee_cal_ro(price):
    """
    计算genius费用RMB
    :param price:
    :return:
    """
    fee_ron = 5
    if price < 30:
        fee_ron = 1
    elif price < 40:
        fee_ron = 1.5
    elif price < 50:
        fee_ron = 2
    elif price < 75:
        fee_ron = 2.5
    elif price < 150:
        fee_ron = 3.5
    return fee_ron * RON_TO_RMB * (1 + VAT["ro"])


def genius_fee_cal_bg(price):
    """
    计算genius费用RMB
    :param price:
    :return:
    """
    fee_bgn = 2
    if price < 12:
        fee_bgn = 0.4
    elif price < 16:
        fee_bgn = 0.6
    elif price < 20:
        fee_bgn = 0.75
    elif price < 30:
        fee_bgn = 1
    elif price < 60:
        fee_bgn = 1.4
    return fee_bgn * BGN_TO_RMB * (1 + VAT["bg"])


def genius_fee_cal_hu(price):
    """
    计算genius费用RMB
    :param price:
    :return:
    """
    fee_huf = 400
    if price < 2400:
        fee_huf = 80
    elif price < 3200:
        fee_huf = 120
    elif price < 4000:
        fee_huf = 160
    elif price < 6000:
        fee_huf = 200
    elif price < 12000:
        fee_huf = 280
    return fee_huf * HUF_TO_RMB * (1 + VAT["hu"])
