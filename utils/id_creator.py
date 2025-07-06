# -*- coding: UTF-8 -*-
'''
@Project     ：em_buy_carts_monitor_backen 
@File        ：id_creator.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-03-03 14:50 
-------------------------------------
'''
import random
import time


def order_id_create():
    """
    :param order_type: 00:免费 01,02,03,04 11,12,13,14
    :return:
    """
    return f"ON{int(time.time())}"


def phone_code_create():
    return str(random.randint(100000, 999999))
