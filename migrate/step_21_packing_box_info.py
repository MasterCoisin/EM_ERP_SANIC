# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：step_20_packing_box_info.py
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
from migrate.step_17_box_type_info import BoxTypeInfo
from migrate.step_19_shipments_order import ShipmentsOrder
from utils.common import to_mongo, get_uuid
from utils.models import ModelManagerOld as ModelManager


class PackingBoxInfo(DynamicDocument):
    campanyId = StringField()
    shop = StringField()
    whId = StringField()
    emReceptionId = StringField()
    packingOrderId = StringField()
    packingInfo = ListField()
    packingSummary = DictField()
    tip = StringField()
    createTime = DateTimeField()
    updateTime = DateTimeField()
    deleted = BooleanField()
    meta = {
        'db_alias': 'new_db',
        'collection': 'packing_box_info',
        "indexes": [
            {
                'fields': ['campanyId', 'emReceptionId'],
                "name": "emReceptionId"
            }
        ]
    }


def main():
    PackingBoxInfo.objects().count()
    data = json.loads(old_packing_box_info_model.objects().to_json())
    adds = []
    box_info = {i.boxId: {
        "boxId": i.boxId,
        "boxName": i.boxName,
        "boxL": i.boxL,
        "boxW": i.boxW,
        "boxH": i.boxH,
        "boxWeight": i.boxWeight
    } for i in BoxTypeInfo.objects(campanyId=CAMPANY_ID)}
    msku_ean = old_listing_model.objects().only("base_info__msku","base_info__ean")
    msku_to_ean = {}
    for i in msku_ean:
        msku_to_ean[i.base_info.get("msku", None)] = i.base_info.get("ean", None)
    for obj in data:
        packing_infos = obj.get("packing_info", [])
        packingInfo = []
        for packing_info in packing_infos:
            msku_in_box = packing_info.get("msku_in_box", {}).values()
            packingInfo.append({
                "boxInfo": box_info[packing_info.get("bx_id", None)],
                "mskuInBox": {
                    msku_to_ean.get(i["msku"], None):i["count"]
                    for i in msku_in_box
                }
            })
        adds.append(
            {
                "tip": obj.get("tip", None),
                "shop": "wl",
                "whId": "41b15e00-1d82-11ef-b71f-3938ce80ebf6",
                "campanyId": CAMPANY_ID,
                "packingOrderId": obj.get("shipments_order_id", None),
                "version": obj.get("version", None),
                "packingInfo": packingInfo,
                "packingSummary": {
                    "eanToInfo": {},
                    "receptionId": None
                },
                "emReceptionId": None,
                "createTime": datetime.datetime.fromtimestamp(obj.get("create_time", None)),
                "updateTime": datetime.datetime.fromtimestamp(obj.get("create_time", None)),
                "deleted": False
            }
        )
    to_mongo(PackingBoxInfo, adds, ["campanyId", "packingOrderId"])


if __name__ == '__main__':
    connect(host="mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin", alias='new_db')
    old_packing_box_info_model = ModelManager.get_model("packing_box_info", "base")
    old_listing_model = ModelManager.get_model("listing", "base")
    main()
