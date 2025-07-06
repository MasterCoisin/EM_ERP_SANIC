# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：step_2_festival.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：迁移festival表
@Date        ：2024-12-19 21:16 
-------------------------------------
'''
import datetime
import json
from loguru import logger
from mongoengine import *

from migrate.constant import CAMPANY_ID
from utils.common import to_mongo
from utils.models import ModelManagerOld as ModelManager


class Festival(DynamicDocument):
    festival_code=StringField(),
    festival_name= StringField(),
    deleted=BooleanField(default=False)
    meta = {
        'db_alias': 'new_db',
        'collection': 'festival',
        "indexes": [
            {
                'fields': ['festival_code'],
                "name": "uni_festival_code"
            }
        ]
    }


def main():
    Festival.objects().count()
    data = json.loads(old_festival_model.objects().only("festival_code", "festival_name", "deleted").to_json())
    for obj in data:
        del obj["_id"]
        obj["campanyId"] = CAMPANY_ID
        obj["createTime"] = datetime.datetime.now()
        obj["updateTime"] = datetime.datetime.now()
    to_mongo(Festival,data,["campanyId","festival_code"])


if __name__ == '__main__':
    connect(host="mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin", alias='new_db')
    old_festival_model = ModelManager.get_model("festival", "base")
    main()