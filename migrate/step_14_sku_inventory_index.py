# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：step_2_sku_inventory_index.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：迁移sku_inventory_index表
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


class SkuInventoryIndex(DynamicDocument):
    campanyId = StringField()
    whId = StringField()
    sku = StringField()
    skuTotalBuy = IntField()
    skuLeft = IntField()
    skuHasSend = IntField()
    skuBuyTimes = IntField()
    skuAvgFee = FloatField()
    skuTotalFee = FloatField()

    skuInBox = IntField()
    skuInTrans = IntField()
    skuDealByUs = IntField()
    skuBeDestroied = IntField()


    deleted = BooleanField(default=False)
    meta = {
        'db_alias': 'new_db',
        'collection': 'sku_inventory_index',
        "indexes": [
            {
                'fields': ['campanyId','whId'],
                "name": "whId"
            },
            {
                'fields': ['campanyId','sku'],
                "name": "sku"
            },
            {
                'fields': ['campanyId','deleted'],
                "name": "deleted"
            }
        ]
    }


class SkuInventoryDetail(DynamicDocument):
    campanyId = StringField()
    whId = StringField()
    sku = StringField()
    skuBatchNumber = IntField()
    skuBatchOrder = IntField()
    skuFee = FloatField()
    skuInboundDate = IntField()
    skuHasSend = BooleanField()
    skuStatus = IntField(help_text="0:在仓库 1:已装箱 2.国际物流在途 3.到海外仓 4.内部处理 5:销毁")
    shipmentsOrderId = StringField()
    packingOrderId = StringField()
    toEan = StringField()
    toMskuBatchNumber = IntField()
    toMskuBatchOrder = IntField()

    tip = StringField(default="")

    meta = {
        'db_alias': 'new_db',
        'collection': 'sku_inventory_detail',
        "indexes": [
            {
                'fields': ['campanyId','whId'],
                "name": "whId"
            },
            {
                'fields': ['campanyId','sku'],
                "name": "sku"
            },
            {
                'fields': ['campanyId',"whId", "sku","skuBatchNumber","skuBatchOrder"],
                "name": "whId_sku_skuBatchNumber_skuBatchOrder"
            },
            {
                'fields': ['campanyId','whId','sku', 'skuBatchNumber', 'skuBatchOrder','hasSend'],
                "name": "whId_sku_skuBatchNumber_skuBatchOrder_hasSend"
            },
            {
                'fields': ['campanyId','deleted'],
                "name": "deleted"
            }
        ]
    }


def refresh_sku_index_data():
    """
    更新sku概览数据
    :return:
    """
    data = SkuInventoryDetail.objects()
    sku_info = {}
    sku_fee = {}
    sku_sku_batch_number = {}
    for line in data:
        r_id = f"{line.sku}_{line.whId}"
        if r_id not in sku_info:
            sku_info[r_id] = {
                "campanyId":CAMPANY_ID,
                "sku": line.sku,
                "whId": line.whId,
                "skuTotalBuy": 0,
                "skuLeft":0,
                "skuHasSend":0,
                "skuInBox":0,
                "skuInTrans":0,
                "skuDealByUs":0,
                "skuBeDestroied":0
            }
            sku_fee[r_id] = []
            sku_sku_batch_number[r_id] = set()
        sku_fee[r_id].append(line.skuFee)
        sku_sku_batch_number[r_id].add(line.skuBatchNumber)
        sku_info[r_id]['skuTotalBuy'] += 1
        # if not line.deleted: 0:在仓库 1:已装箱 2.国际物流在途 3.到海外仓 4.内部处理 5:销毁
        if line.skuStatus==0:
            sku_info[r_id]['skuLeft'] += 1
        elif line.skuStatus==1:
            sku_info[r_id]['skuInBox'] += 1
        elif line.skuStatus==2:
            sku_info[r_id]['skuInTrans'] += 1
        elif line.skuStatus==3:
            sku_info[r_id]['skuHasSend'] += 1
        elif line.skuStatus==4:
            sku_info[r_id]['skuDealByUs'] += 1
        elif line.skuStatus==5:
            sku_info[r_id]['skuBeDestroied'] += 1

    for r_id, v in sku_fee.items():
        sku_info[r_id]['skuAvgFee'] = sum(v) / len(v) if v else 0
        sku_info[r_id]["skuTotalFee"] = sum(v)
    for r_id, v in sku_sku_batch_number.items():
        sku_info[r_id]['skuBuyTimes'] = len(v)

    to_mongo(m=SkuInventoryIndex, datas=list(sku_info.values()), filters=["campanyId","whId", "sku"])


def main():
    SkuInventoryIndex.objects().count()
    SkuInventoryDetail.objects().count()
    data = old_sku_inventory_detail_model.objects()
    ups = []
    for obj in data:
        ups.append({
            "campanyId": CAMPANY_ID,
            "whId": obj.sku_wh_id,
            "sku": obj.sku,
            "skuBatchNumber": obj.sku_batch_number,
            "skuBatchOrder": obj.sku_batch_order,
            "skuFee": obj.sku_fee,
            "skuInboundDate": obj.sku_inbound_date,
            "tip": "",
            "skuHasSend":obj.deleted,
            "skuStatus":0,
            "shipmentsOrderId":None,
            "packingOrderId":None,
            "toEan":None,
            "toMskuBatchNumber":None,
            "toMskuBatchOrder":None
        })

    to_mongo(SkuInventoryDetail, ups, ["campanyId","whId", "sku","skuBatchNumber","skuBatchOrder"])
    refresh_sku_index_data()


def int_to_timestamp(date_int):
    # 将整数转换为字符串，方便处理
    date_str = str(date_int)

    # 解析出年、月、日
    year = int(date_str[0:4])
    month = int(date_str[4:6])
    day = int(date_str[6:8])

    # 创建 datetime 对象
    dt = datetime.datetime(year, month, day)

    # 将 datetime 对象转换为时间戳（UTC 时间）
    timestamp = dt.timestamp()

    return int(timestamp)

if __name__ == '__main__':
    connect(host="mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin", alias='new_db')
    old_sku_inventory_index_model = ModelManager.get_model("sku_inventory_index", "base")
    old_sku_inventory_detail_model = ModelManager.get_model("sku_inventory_detail", "base")
    refresh_sku_index_data()
    # main()
    # objs = SkuInventoryDetail.objects().only("skuBatchNumber")
    # for obj in objs:
    #     skuBatchNumber = int_to_timestamp(obj.skuBatchNumber)
    #     obj.update(skuBatchNumber=skuBatchNumber)