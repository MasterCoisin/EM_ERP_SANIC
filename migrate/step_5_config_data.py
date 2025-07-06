# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：step_1_config_data.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：迁移config_data表
@Date        ：2024-12-19 21:16 
-------------------------------------
'''
import json
from loguru import logger
from mongoengine import *

from utils.common import to_mongo
from utils.models import ModelManagerOld as ModelManager


class ConfigData(DynamicDocument):
    config_data_id = StringField()
    meta = {
        'db_alias': 'new_db',
        'collection': 'config_data',
        "indexes": [
            {
                'fields': ['field_name'],
                "name": "uni_field_name"
            }
        ]
    }


def main():
    """"config_data_country": StringField(),
            "config_data_platform": StringField(),
            "config_data_id": StringField(),
            "config_data_name": StringField(),
            "company_info": DictField(),
            "rep": StringField(),
            "userInfo1688": StringField(help_text="1688买家ID"),
            "token1688": StringField(help_text="1688买家授权token"),
            "deleted": BooleanField(default=False)"""
    ConfigData.objects().count()
    data = json.loads(old_config_data_model.objects().to_json())
    for obj in data:
        del obj["_id"]
    to_mongo(ConfigData,data,["field_name"])


if __name__ == '__main__':
    connect(host="mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin", alias='new_db')
    old_config_data_model = ModelManager.get_model("config_data", "base")
    main()