# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：step_2_supplier.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：迁移supplier表
@Date        ：2024-12-19 21:16 
-------------------------------------
'''
import datetime
import json
from loguru import logger
from mongoengine import *

from migrate.constant import CAMPANY_ID
from utils.common import to_mongo, get_uuid
from utils.format_tool import str_to_float, str_to_int
from utils.models import ModelManagerOld as ModelManager


class Supplier(DynamicDocument):
    uuid = StringField()
    oldId = StringField()
    name = StringField()
    sellerMemberId = StringField()
    unifiedSocialCreditCode = StringField()
    url = StringField()

    createTime = DateTimeField(default=datetime.datetime.now)
    updateTime = DateTimeField(default=datetime.datetime.now)
    deleted = BooleanField(default=False)
    meta = {
        'db_alias': 'new_db',
        'collection': 'supplier',
        "indexes": [
            {
                'fields': ['uuid'],
                "name": "uuid"
            },
            {
                'fields': ['createTime'],
                "name": "createTime"
            }
        ]
    }


def main():
    Supplier.objects().count()
    data = old_supplier_model.objects()
    ups = []
    for obj in data:
        ups.append({
            "campanyId":CAMPANY_ID,
            "uuid": get_uuid(),
            "oldId":str(obj.id),
            "name": obj.name,
            "sellerMemberId": obj.seller_member_id,
            #"unifiedSocialCreditCode": obj.unifiedSocialCreditCode,
            "url": obj.url,

            "createTime": datetime.datetime.now(),
            "updateTime": datetime.datetime.now(),
            "deleted": obj.deleted
        })
    to_mongo(Supplier, ups, ["campanyId","uuid"])


if __name__ == '__main__':
    connect(host="mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin", alias='new_db')
    old_supplier_model = ModelManager.get_model("supplier", "base")
    main()
