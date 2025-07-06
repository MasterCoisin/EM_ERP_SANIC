# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：step_1_shipments_order.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：迁移shipments_order表
@Date        ：2024-12-19 21:16 
-------------------------------------
'''
import datetime
import json
from loguru import logger
from mongoengine import *

from migrate.constant import CAMPANY_ID
from migrate.step_14_sku_inventory_index import SkuInventoryDetail
from migrate.step_15_msku_inventory_index import MskuInventoryDetail
from utils.common import to_mongo
from utils.models import ModelManagerOld as ModelManager


class ShipmentsOrder(DynamicDocument):
    campanyId = StringField()
    shop = StringField()
    sendFromWhId = StringField()
    sendToWhId = StringField()
    shipmentsOrderId = StringField()
    packingOrderId = StringField()
    emReceptionId = StringField()
    status = IntField()
    eanInfo = ListField()
    domesticLogisticsInfo = DictField()
    internationalLogisticsInfo = DictField()
    createTime = DateTimeField()
    updateTime = DateTimeField()
    deleted = BooleanField()
    meta = {
        'db_alias': 'new_db',
        'collection': 'shipments_order',
        "indexes": [
            {
                'fields': ['campanyId', 'shipmentsOrderId'],
                "name": "shipmentsOrderId"
            }
        ]
    }


def main():
    ShipmentsOrder.objects().count()
    data = json.loads(old_shipments_order_model.objects(status=4).to_json())
    adds = []
    for obj in data:
        mskus = obj.get("mskus", [])
        msku_ean = old_listing_model.objects(base_info__msku__in=list(mskus.keys())).only("base_info__msku",
                                                                                          "base_info__ean")
        msku_to_ean = {}
        for i in msku_ean:
            msku_to_ean[i.base_info.get("msku", None)] = i.base_info.get("ean", None)
        adds.append({
            "campanyId": CAMPANY_ID,
            "shop": obj.get("shop", None),
            "shipmentsOrderId": obj.get("shipments_order_id", None),
            "packingOrderId": None,
            "emReceptionId": None,
            "status": 4,
            "sendFromWhId": obj.get("send_from", None),
            "sendToWhId": obj.get("send_to", None),
            "eanInfo": [
                {
                    "ean": msku_to_ean.get(k, None),
                    "count": v
                } for k, v in mskus.items()
            ],
            "domesticLogisticsInfo": {
                "lpId": obj.get("domestic_ogistics_info", {}).get("lp_id", None),
                "price": obj.get("domestic_ogistics_info", {}).get("price", None),
                "priceSure": obj.get("domestic_ogistics_info", {}).get("price_sure", None),
                "status": obj.get("domestic_ogistics_info", {}).get("status", None),
                "t": obj.get("domestic_ogistics_info", {}).get("t", None),
                "tNo": obj.get("domestic_ogistics_info", {}).get("t_no", None),
                "tNoSure": obj.get("domestic_ogistics_info", {}).get("t_no_sure", None)
            },
            "internationalLogisticsInfo": {
                "lpId": obj.get("international_ogistics_info", {}).get("lp_id", None),
                "price": obj.get("international_ogistics_info", {}).get("price", None),
                "priceSure": obj.get("international_ogistics_info", {}).get("price_sure", None),
                "status": obj.get("international_ogistics_info", {}).get("status", None),
                "t": obj.get("international_ogistics_info", {}).get("t", None),
                "tNo": obj.get("international_ogistics_info", {}).get("t_no", None),
                "tNoSure": obj.get("international_ogistics_info", {}).get("t_no_sure", None)
            },
            "deleted": False,
            "createTime": datetime.datetime.fromtimestamp(obj.get("create_time", None)),
            "updateTime": datetime.datetime.fromtimestamp(obj.get("international_ogistics_info", {}).get("t", None)[3]),
        }
        )
        day_ = datetime.datetime.fromtimestamp(obj.get("international_ogistics_info", {}).get("t", None)[3])
        version = int(f"{day_.year}{day_.month:0>2}{day_.day:0>2}")
        SkuInventoryDetail.objects(campanyId=CAMPANY_ID,toMskuBatchNumber=version).update(shipmentsOrderId=obj.get("shipments_order_id", None))
        MskuInventoryDetail.objects(campanyId=CAMPANY_ID,mskuBatchNumber=version).update(shipmentsOrderId=obj.get("shipments_order_id", None))
    to_mongo(ShipmentsOrder, adds, ["campanyId", "shipmentsOrderId"])


if __name__ == '__main__':
    connect(host="mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin", alias='new_db')
    old_shipments_order_model = ModelManager.get_model("shipments_order", "base")
    old_listing_model = ModelManager.get_model("listing", "base")
    main()
