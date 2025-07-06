# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：step_1_em_category.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：迁移em_category表
@Date        ：2024-12-19 21:16 
-------------------------------------
'''
import json
from loguru import logger
from mongoengine import *

from utils.common import to_mongo
from utils.models import ModelManager


class EmCategory(DynamicDocument):
    em_category_id = StringField()
    meta = {
        'db_alias': 'new_db',
        'collection': 'em_category',
        "indexes": [
            {
                'fields': ['em_category_id'],
                "name": "uni_em_category_id"
            }
        ]
    }


def main():
    """"em_category_country": StringField(),
            "em_category_platform": StringField(),
            "em_category_id": StringField(),
            "em_category_name": StringField(),
            "company_info": DictField(),
            "rep": StringField(),
            "userInfo1688": StringField(help_text="1688买家ID"),
            "token1688": StringField(help_text="1688买家授权token"),
            "deleted": BooleanField(default=False)"""
    EmCategory.objects().count()
    data = json.loads(old_em_category_model.objects().to_json())
    for obj in data:
        del obj["_id"]
    to_mongo(EmCategory,data,["category_id"])


if __name__ == '__main__':
    connect(host="mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin", alias='new_db')
    old_em_category_model = ModelManager.get_model("em_category", "base")
    main()