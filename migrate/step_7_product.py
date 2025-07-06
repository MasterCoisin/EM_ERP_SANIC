# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：step_7_product.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：迁移product表
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
from utils.common import to_mongo, to_float
from utils.models import ModelManagerOld as ModelManager


class Product(DynamicDocument):
    sku = StringField()
    productName = StringField()
    url1688 = StringField()
    images = ListField()
    tip = StringField()
    competitorUrls = StringField()
    length = FloatField()
    width = FloatField()
    height = FloatField()
    weight = FloatField()
    volumeWeight: FloatField()
    weighing: FloatField()
    # purchaseCost = FloatField()
    supplierInfo = DynamicField()

    createTime = DateTimeField(default=datetime.datetime.now)
    updateTime = DateTimeField(default=datetime.datetime.now)
    deleted = BooleanField(default=False)
    meta = {
        'db_alias': 'new_db',
        'collection': 'product',
        "indexes": [
            {
                'fields': ['sku'],
                "name": "sku"
            },
            {
                'fields': ['createTime'],
                "name": "createTime"
            }
        ]
    }


def main():
    Product.objects().count()
    data = old_product_model.objects()
    ups = []
    for obj in data:
        ups.append({
            "campanyId":CAMPANY_ID,
            "sku": obj.sku,
            "productName": obj.product_profit_cal_data.get("product_name", None),
            "url1688": obj.product_profit_cal_data.get("url_1688", None),
            "images": obj.info_1688.get("images", []),
            "tip": obj.product_profit_cal_data.get("tip", None),
            "competitorUrls": obj.product_profit_cal_data.get("competitors_url", None),
            "length": to_float(obj.product_profit_cal_data.get("length", None)),
            "width": to_float(obj.product_profit_cal_data.get("width", None)),
            "height": to_float(obj.product_profit_cal_data.get("height", None)),
            "weight": to_float(obj.product_profit_cal_data.get("weight", None)),
            "volumeWeight": to_float(obj.cal_result.get("volume_weight", None)),
            "weighing": to_float(obj.cal_result.get("weighing", None)),
            "supplierInfo": {
                "purchaseCost": to_float(obj.product_attributes.get("supplier_info",{}).get("prices", [{}])[0].get("price", None)),
                "purchaseTip": obj.product_attributes.get("supplier_info", {}).get("cai_gou_tip", None),
                "skuInfoMap": obj.product_attributes.get("supplier_info", {}).get("sku_info_map", []),
                "specId": obj.product_attributes.get("supplier_info", {}).get("spec_id", {}),
                "supplierId": Supplier.objects(
                    oldId=obj.product_attributes.get("supplier_info", {}).get("supplier_id", None)).only(
                    "uuid").first().uuid if obj.product_attributes.get("supplier_info", {}).get("supplier_id",
                                                                                                None) else None
            },
            "createTime": datetime.datetime.now(),
            "updateTime": datetime.datetime.now(),
            "deleted": obj.deleted
        })
        time.sleep(0.01)
    to_mongo(Product, ups, ["campanyId","sku"])

if __name__ == '__main__':
    connect(host="mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin", alias='new_db')
    old_product_model = ModelManager.get_model("product", "base")
    main()
