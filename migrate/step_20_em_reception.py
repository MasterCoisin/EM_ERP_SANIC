# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：step_20_em_reception.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-05-09 15:46 
-------------------------------------
'''

import datetime
import json
from loguru import logger
from mongoengine import *

from migrate.constant import CAMPANY_ID
from migrate.step_14_sku_inventory_index import SkuInventoryDetail
from migrate.step_15_msku_inventory_index import MskuInventoryDetail
from migrate.step_19_shipments_order import ShipmentsOrder
from utils.common import to_mongo, get_uuid
from utils.models import ModelManagerOld as ModelManager


class EmReception(DynamicDocument):
    campanyId = StringField()
    shop = StringField()
    emReceptionId = StringField()
    sendFromWhId = StringField()
    sendToWhId = StringField()
    shipmentsOrderId = StringField()
    packingOrderId = StringField()
    receptionId = StringField()
    hasSend = BooleanField()
    eanInfo = ListField()
    createTime = DateTimeField()
    updateTime = DateTimeField()
    deleted = BooleanField()
    meta = {
        'db_alias': 'new_db',
        'collection': 'em_reception',
        "indexes": [
            {
                'fields': ['campanyId', 'emReceptionId'],
                "name": "emReceptionId"
            }
        ]
    }


def main():
    EmReception.objects().count()
    data = json.loads(old_em_reception_model.objects().to_json())
    adds = []
    for obj in data:
        emReceptionId = get_uuid()
        adds.append(
            {
                "campanyId": CAMPANY_ID,
                "shop": obj.get("shop_id", None),
                "emReceptionId": emReceptionId,
                "packingOrderId": None,
                "shipmentsOrderId": obj.get("shipments_order_id", None),
                "sendFromWhId": obj.get("send_from", None),
                "sendToWhId": obj.get("send_to", None),
                "receptionId": obj.get("reception_id", None),
                "hasSend": obj.get("has_send", None),
                "eanInfo": [
                    {
                        "ean": i["ean"],
                        "count": i["count"],
                        "uploadStatus": 1
                    } for i in obj.get("listing_data",[])
                ],
                "createTime": datetime.datetime.fromtimestamp(obj.get("create_time", None)),
                "updateTime": datetime.datetime.fromtimestamp(obj.get("create_time", None)),
                "deleted": False
            }
        )
        ShipmentsOrder.objects(campanyId=CAMPANY_ID,shipmentsOrderId=obj.get("shipments_order_id", None)).update(emReceptionId=emReceptionId)

    to_mongo(EmReception, adds, ["campanyId", "shipmentsOrderId"])


if __name__ == '__main__':
    connect(host="mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin", alias='new_db')
    old_em_reception_model = ModelManager.get_model("reception_order", "base")
    main()
