# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：format_tool.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024-12-27 22:51 
-------------------------------------
'''
from datetime import datetime
from hashlib import md5


def str_to_md5(s):
    return str(md5(s.encode()).hexdigest())


def str_to_int():
    pass


def str_to_float(s):
    if s:
        return float(str(s))
    else:
        return None


def str_to_datetime(time_str):
    # 指定时间格式
    format_str = "%Y-%m-%d %H:%M:%S"
    # 执行转换
    return datetime.strptime(time_str, format_str)
