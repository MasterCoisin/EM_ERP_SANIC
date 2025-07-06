# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：step_1_logistics_provider.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：迁移logistics_provider表
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


class LogisticsProvider(DynamicDocument):
    campanyId = StringField()
    lpId = StringField()
    lpName = StringField()
    lpPassword = StringField()
    lpExpireTime = IntField()
    lpToken = StringField()
    createTime = DateTimeField()
    updateTime = DateTimeField()
    meta = {
        'db_alias': 'new_db',
        'collection': 'logistics_provider',
        "indexes": [
            {
                'fields': ['campanyId', 'lpId'],
                "name": "lpId"
            }
        ]
    }


def main():
    LogisticsProvider.objects().count()
    data = json.loads(old_logistics_provider_model.objects().to_json())
    adds = []
    for obj in data:
        adds.append({
            "campanyId": CAMPANY_ID,
            "lpId": obj.get("lp_id",None),
            "lpName": obj.get("lp_name",None),
            "deleted": obj.get("deleted",None),
            "lpPassword": obj.get("lp_password",None),
            "lpExpireTime": obj.get("lp_expire_time",None),
            "lpToken": obj.get("lp_token",None),
            "createTime": datetime.datetime.now(),
            "updateTime": datetime.datetime.now(),
        })
    to_mongo(LogisticsProvider, adds, ["campanyId", "lpId"])


if __name__ == '__main__':
    connect(host="mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin", alias='new_db')
    old_logistics_provider_model = ModelManager.get_model("logistics_provider", "base")
    main()
