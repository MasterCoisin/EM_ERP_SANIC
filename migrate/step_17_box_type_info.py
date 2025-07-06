# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：step_1_box_type_info.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：迁移box_type_info表
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


class BoxTypeInfo(DynamicDocument):
    campanyId = StringField()
    boxId = StringField()
    meta = {
        'db_alias': 'new_db',
        'collection': 'box_type_info',
        "indexes": [
            {
                'fields': ['campanyId', 'boxId'],
                "name": "boxId"
            }
        ]
    }


def main():
    BoxTypeInfo.objects().count()
    data = json.loads(old_box_type_info_model.objects().to_json())
    adds = []
    for obj in data:
        adds.append({
            "boxName": obj.get("bx_name", None),
            "boxL": obj.get("bx_l", None),
            "boxW": obj.get("bx_w", None),
            "boxH": obj.get("bx_h", None),
            "boxWeight": obj.get("bx_weight", None),
            "deleted": False,
            "campanyId": CAMPANY_ID,
            "boxId": obj.get("bx_id", None),
            "createTime": datetime.datetime.now(),
            "updateTime": datetime.datetime.now(),
        })
    to_mongo(BoxTypeInfo, adds, ["campanyId", "boxId"])


if __name__ == '__main__':
    connect(host="mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin", alias='new_db')
    old_box_type_info_model = ModelManager.get_model("box_type_info", "base")
    main()
