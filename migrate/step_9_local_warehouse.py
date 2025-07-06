# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：step_1_local_warehouse.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：迁移local_warehouse表
@Date        ：2024-12-19 21:16 
-------------------------------------
'''
import datetime
import json
import time

from loguru import logger
from mongoengine import *

from migrate.constant import CAMPANY_ID
from utils.common import to_mongo
from utils.models import ModelManagerOld as ModelManager


class LocalWarehouse(DynamicDocument):
    whId = StringField()
    whName = StringField()

    createTime = DateTimeField(default=datetime.datetime.now)
    updateTime = DateTimeField(default=datetime.datetime.now)
    deleted = BooleanField(default=False)
    meta = {
        'db_alias': 'new_db',
        'collection': 'local_warehouse',
        "indexes": [
            {
                'fields': ['local_warehouse_id'],
                "name": "uni_local_warehouse_id"
            }
        ]
    }


def main():
    LocalWarehouse.objects().count()
    LocalWarehouse.objects().count()
    data = old_local_warehouse_model.objects()
    ups = []
    for obj in data:
        ups.append({
            "campanyId":CAMPANY_ID,
            "whId": obj.wh_id,
            "whName": obj.wh_name,

            "createTime": datetime.datetime.now(),
            "updateTime": datetime.datetime.now(),
            "deleted": obj.deleted
        })
        time.sleep(0.01)
    to_mongo(LocalWarehouse, ups, ["campanyId","whId"])


if __name__ == '__main__':
    connect(host="mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin", alias='new_db')
    old_local_warehouse_model = ModelManager.get_model("local_warehouse", "base")
    main()