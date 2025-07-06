# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BACKEN 
@File        ：constant_tool.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024-07-14 22:08 
-------------------------------------
'''
import datetime


def get_days():
    org_day = datetime.datetime(year=2024, month=7, day=14)
    end_day = datetime.datetime(year=2025, month=7, day=14)
    res = []
    while org_day <= end_day:
        res.append(f"{org_day.year}{org_day.month:0>2}{org_day.day:0>2}")
        org_day += datetime.timedelta(days=1)
    return res
