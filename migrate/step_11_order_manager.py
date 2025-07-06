# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：step_1_order_manager.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：迁移order_manager表
@Date        ：2024-12-19 21:16 
-------------------------------------
'''
import datetime
import json
import time

from loguru import logger
from mongoengine import *

from migrate.constant import CAMPANY_ID
from migrate.step_6_supplier import Supplier
from utils.common import to_mongo
from utils.models import ModelManagerOld as ModelManager


class OrderManager(DynamicDocument):
    orderId = StringField()
    purchaseOrderId = StringField()
    supplierUuid = StringField()
    status = IntField()
    tradeInfo = DictField()

    createTime = DateTimeField(default=datetime.datetime.now)
    updateTime = DateTimeField(default=datetime.datetime.now)
    deleted = BooleanField(default=False)
    meta = {
        'db_alias': 'new_db',
        'collection': 'order_manager',
        "indexes": [
            {
                'fields': ['orderId'],
                "name": "orderId"
            }
        ]
    }


def main():
    OrderManager.objects().count()
    OrderManager.objects().count()
    data = old_order_manager_model.objects()
    ups = []
    for obj in data:
        obj_ = Supplier.objects(
            oldId=obj.supplier_id).only(
            "uuid").first()
        ups.append({
            "campanyId": CAMPANY_ID,
            "orderId": obj.order_id,
            "purchaseOrderId": obj.purchase_order_id,
            "supplierUuid": obj_.uuid,
            "tradeInfo": obj.tradeInfo,

            "createTime": datetime.datetime.now(),
            "updateTime": datetime.datetime.now(),
            "deleted": False
        })
        time.sleep(0.01)
    to_mongo(OrderManager, ups, ["campanyId","orderId"])


if __name__ == '__main__':
    connect(host="mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin", alias='new_db')
    old_order_manager_model = ModelManager.get_model("order_manager", "base")
    main()