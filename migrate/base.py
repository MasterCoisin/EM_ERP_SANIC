# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：base.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024-12-19 21:21 
-------------------------------------
'''
from loguru import logger
from mongoengine import *
from utils.models import ModelManager


class NewCollection(DynamicDocument):
    meta = {
        'db_alias': 'new_db',
        'collection': '',
        "indexes": [
            {
                'fields': [''],
                "name": ""
            }
        ]
    }


if __name__ == '__main__':
    connect(host="mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin", db='new_db')
    shop_model = ModelManager.get_model("shop", "base")
