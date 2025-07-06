# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：step_1_shop.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：迁移shop表
@Date        ：2024-12-19 21:16 
-------------------------------------
'''
import json
from loguru import logger
from mongoengine import *

from utils.common import to_mongo
from utils.models import ModelManagerOld as ModelManager


class Shop(DynamicDocument):
    shop_id = StringField()
    meta = {
        'db_alias': 'new_db',
        'collection': 'shop',
        "indexes": [
            {
                'fields': ['shop_id'],
                "name": "uni_shop_id"
            }
        ]
    }


def main():
    """"shop_country": StringField(),
            "shop_platform": StringField(),
            "shop_id": StringField(),
            "shop_name": StringField(),
            "company_info": DictField(),
            "rep": StringField(),
            "userInfo1688": StringField(help_text="1688买家ID"),
            "token1688": StringField(help_text="1688买家授权token"),
            "deleted": BooleanField(default=False)"""
    Shop.objects().count()
    data = json.loads(old_shop_model.objects().only("shop_id", "shop_name", "company_info", "rep", "token1688", "deleted").to_json())
    for obj in data:
        del obj["_id"]
    to_mongo(Shop,data,["shop_id"])


if __name__ == '__main__':
    connect(host="mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin", alias='new_db')
    old_shop_model = ModelManager.get_model("shop", "base")
    main()