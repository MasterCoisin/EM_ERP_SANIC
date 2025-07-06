# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：step_7_purchase_orders.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：迁移purchase_orders表
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
from utils.common import to_mongo, to_float, get_1688_product_id
from utils.models import ModelManagerOld as ModelManager

class PurchaseOrders(DynamicDocument):
    purchaseOrderId = StringField()
    status = IntField()
    orders = DictField()

    createTime = DateTimeField(default=datetime.datetime.now)
    updateTime = DateTimeField(default=datetime.datetime.now)
    deleted = BooleanField(default=False)
    meta = {
        'db_alias': 'new_db',
        'collection': 'purchase_orders',
        "indexes": [
            {
                'fields': ['purchaseOrderId'],
                "name": "purchaseOrderId"
            },
            {
                'fields': ['status'],
                "name": "status"
            },
            {
                'fields': ['createTime'],
                "name": "createTime"
            }
        ]
    }


def main():
    PurchaseOrders.objects().count()
    data = old_purchase_orders_model.objects()
    ups = []
    for obj in data:
        orders_new = {}
        for k, v in obj.orders.items():
            obj_ = Supplier.objects(
                oldId=k).only(
                "uuid", "name").first()
            v["supplier"] = {
                "uuid": obj_.uuid,
                "name": obj_.name
            }
            v["deleted"] = False
            # shop_id
            v["shopId"] = v.get("shop_id","wl")
            v["addressId"] = v.get("address_id", None)
            v["is1688"] = v.get("is_1688", None)
            for f in ["shop_id","address_id","is_1688"]:
                if f in v:
                    del v[f]
            # order_info
            for f in ["has_fapiao","has_kaipiao","has_print_fapiao"]:
                v["order_info"][f] = v["order_info"].get(f,False)
            if "address_id" in v["order_info"]:
                del v["order_info"]["address_id"]
            # skus
            v["skus"] = [
                {"count": int(i["count"]), "purchaseCost": float(i["price"]) if i.get("price", None) else None,
                 "productName": i["product_name"],
                 "productUrl": i["product_url"], "sku": i["sku"], "images": i["images"], "specId": i["spec_id"],
                 "offerId": i["offer_id"] if i.get("offer_id", None) else get_1688_product_id(i["product_url"]),
                 "fee": i.get("fee", None),
                 "inboundCount": i.get("inbound_count", None),
                 "inboundWarehouseId": i.get("inbound_warehouse_id", None),"deleted":False } for i in
                v["skus"]
            ]
            orders_new[obj_.uuid] = v
        ups.append({
            "campanyId":CAMPANY_ID,
            "purchaseOrderId": obj.purchase_order_id,
            "status": obj.status,
            "orders": orders_new,
            "createTime": datetime.datetime.fromtimestamp(obj.create_time),
            "updateTime": datetime.datetime.now(),
            "deleted": obj.status == -1
        })
        time.sleep(0.01)
    to_mongo(PurchaseOrders, ups, ["campanyId","purchaseOrderId"])


if __name__ == '__main__':
    connect(host="mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin", alias='new_db')
    old_purchase_orders_model = ModelManager.get_model("purchase_orders", "base")
    main()
