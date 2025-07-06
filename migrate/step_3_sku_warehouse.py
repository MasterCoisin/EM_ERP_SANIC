# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：step_3_sku_warehouse.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024-12-27 22:02 
-------------------------------------
'''
import json
from loguru import logger
from mongoengine import *
from tqdm import tqdm

from utils.common import to_mongo
from utils.models import ModelManagerOld as ModelManager


class SkuWarehouse(DynamicDocument):
    sku=StringField(),
    meta = {
        'db_alias': 'new_db',
        'collection': 'sku_warehouse',
        "indexes": [
            {
                'fields': ['sku'],
                "name": "uni_sku"
            }
        ]
    }


def main():
    SkuWarehouse.objects().count()
    data = json.loads(old_sku_warehouse_model.objects().only("sku").to_json())
    for obj in data:
        del obj["_id"]
    per = 5000
    for i in tqdm(range(len(data)//per+1)):
        if data[i*per:(i+1)*per]:
            to_mongo(SkuWarehouse,data[i*per:(i+1)*per],["sku"])

def remove_sku():
    objs = old_product_model.objects().only("sku")
    skus = []
    for obj in objs:
        if obj.sku:
            if obj.sku not in skus:
                skus.append(obj.sku)
            else:
                print(obj.sku)
    print(SkuWarehouse.objects(sku__in=skus).delete())
if __name__ == '__main__':
    connect(host="mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin", alias='new_db')
    old_sku_warehouse_model = ModelManager.get_model("sku_warehouse", "base")
    old_product_model = ModelManager.get_model("product", "base")
    main()
    remove_sku()