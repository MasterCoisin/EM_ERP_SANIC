# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：step_1_overseas_warehouse.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：迁移overseas_warehouse表
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


class OverseasWarehouse(DynamicDocument):
    whId = StringField()
    whName = StringField()

    createTime = DateTimeField(default=datetime.datetime.now)
    updateTime = DateTimeField(default=datetime.datetime.now)
    deleted = BooleanField(default=False)
    meta = {
        'db_alias': 'new_db',
        'collection': 'overseas_warehouse',
        "indexes": [
            {
                'fields': ['overseas_warehouse_id'],
                "name": "uni_overseas_warehouse_id"
            }
        ]
    }


def main():
    OverseasWarehouse.objects().count()
    OverseasWarehouse.objects().count()
    data = old_overseas_warehouse_model.objects()
    ups = []
    for obj in data:
        ups.append({
            "campanyId": CAMPANY_ID,
            "whId": obj.wh_id,
            "whName": obj.wh_name,

            "createTime": datetime.datetime.now(),
            "updateTime": datetime.datetime.now(),
            "deleted": obj.deleted
        })
        time.sleep(0.01)
    to_mongo(OverseasWarehouse, ups, ["campanyId","whId"])


if __name__ == '__main__':
    connect(host="mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin", alias='new_db')
    old_overseas_warehouse_model = ModelManager.get_model("overseas_warehouse", "base")
    main()