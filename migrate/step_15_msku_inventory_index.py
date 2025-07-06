# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：step_2_msku_inventory_index.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：迁移msku_inventory_index表
@Date        ：2024-12-19 21:16 
-------------------------------------
'''
import datetime
import json
from loguru import logger
from mongoengine import *

from migrate.constant import CAMPANY_ID
from migrate.step_14_sku_inventory_index import SkuInventoryIndex, SkuInventoryDetail, int_to_timestamp
from utils.common import to_mongo, get_uuid
from utils.format_tool import str_to_float, str_to_int
from utils.models import ModelManagerOld as ModelManager



class MskuInventoryIndex(DynamicDocument):
    campanyId=StringField()
    whId = StringField()
    ean = StringField()
    mskuTotalSent = IntField()
    mskuLeft = IntField()
    mskuInTrans = IntField()
    mskuHasPurchased = IntField()
    mskuHasLosed = IntField()
    mskuHasDestroyed = IntField()
    mskuSendTimes = IntField()
    mskuFinallInboundDate = IntField()
    mskuFirstInboundDate = IntField()
    mskuAvgFee = FloatField()
    mskuTotalFee = FloatField()
    mskuAvgHeadFee = FloatField()
    mskuTotalHeadFee = FloatField()
    mskuAvgBuyAndHeadFee = FloatField()
    mskuTotalBuyAndHeadFee = FloatField()

    deleted = BooleanField(default=False)
    meta = {
        'db_alias': 'new_db',
        'collection': 'msku_inventory_index',
        "indexes": [
            {
                'fields': ['campanyId','whId'],
                "name": "whId"
            },
            {
                'fields': ['campanyId','ean'],
                "name": "ean"
            },
            {
                'fields': ['campanyId','deleted'],
                "name": "deleted"
            }
        ]
    }


class MskuInventoryDetail(DynamicDocument):
    campanyId=StringField()
    whId = StringField()
    ean = StringField()
    mskuBatchNumber = IntField()
    mskuBatchOrder = IntField()
    mskuFee = FloatField()
    mskuHeadFee = FloatField()
    mskuBuyAndHeadFee = FloatField()
    mskuInboundDate = IntField()
    skusInfo = ListField()
    status = IntField(default=0,help_text="0:在库 1:售出 2:在途 3:入仓丢失 4:销毁")
    buyCountry = StringField()
    orderId = IntField()
    statusVersion = IntField()
    tip = StringField(default="")
    meta = {
        'db_alias': 'new_db',
        'collection': 'msku_inventory_detail',
        "indexes": [
            {
                'fields': ['campanyId','whId'],
                "name": "whId"
            },
            {
                'fields': ['campanyId','ean'],
                "name": "ean"
            },
            {
                'fields': ['campanyId','orderId', 'buyCountry'],
                "name": "orderId_buyCountry"
            },
            {
                'fields': ['campanyId','statusVersion'],
                "name": "statusVersion"
            },
            {
                'fields': ['campanyId',"whId", "ean", "mskuBatchNumber", "mskuBatchOrder"],
                "name": "whId_ean_mskuBatchNumber_mskuBatchOrder"
            },
            {
                'fields': ['campanyId','whId', 'ean', 'mskuBatchNumber', 'mskuBatchOrder', 'hasSend'],
                "name": "whId_ean_mskuBatchNumber_mskuBatchOrder_hasSend"
            },
            {
                'fields': ['campanyId','deleted'],
                "name": "deleted"
            }
        ]
    }


def refresh_msku_index_data():
    """
    更新msku概览数据
    :return:
    """
    data = MskuInventoryDetail.objects()
    msku_info = {}
    msku_fee = {}
    msku_head_fee = {}
    msku_buy_and_head_fee = {}
    msku_msku_batch_number = {}
    for line in data:
        r_id = f"{line.ean}_{line.whId}"
        if r_id not in msku_info:
            msku_info[r_id] = {
                "campanyId": CAMPANY_ID,
                "ean": line.ean,
                "whId": line.whId,
                "mskuLeft":0,
                "mskuInTrans":0,
                "mskuTotalSent":0,
                "mskuHasPurchased": 0,
                "mskuHasLosed": 0,
                "mskuHasDestroyed": 0,
                "mskuFirstInboundDate":None,
                "mskuFinallInboundDate":None
            }
            msku_fee[r_id] = []
            msku_head_fee[r_id] = []
            msku_buy_and_head_fee[r_id] = []
            msku_msku_batch_number[r_id] = set()
        if line.status!=2:
            msku_fee[r_id].append(line.mskuFee)
            msku_head_fee[r_id].append(line.mskuHeadFee)
            msku_buy_and_head_fee[r_id].append(line.mskuBuyAndHeadFee)
        msku_msku_batch_number[r_id].add(line.mskuBatchNumber)
        msku_info[r_id]['mskuTotalSent'] += 1
        # 0:在库 1:售出 2:在途 3:入仓丢失 4:销毁

        if line.status==1:
            msku_info[r_id]['mskuHasPurchased'] += 1
        elif line.status==0:
            msku_info[r_id]['mskuLeft'] += 1
        elif line.status==2:
            msku_info[r_id]['mskuInTrans'] += 1
        elif line.status==3:
            msku_info[r_id]['mskuHasLosed'] += 1
        elif line.status==4:
            msku_info[r_id]['mskuHasDestroyed'] += 1
        if line.status != 2:
            if not msku_info[r_id]["mskuFirstInboundDate"]:
                msku_info[r_id]["mskuFirstInboundDate"]=line.mskuInboundDate
            else:
                msku_info[r_id]["mskuFirstInboundDate"] = min([msku_info[r_id]["mskuFirstInboundDate"] ,line.mskuInboundDate])
            if not msku_info[r_id]["mskuFinallInboundDate"]:
                msku_info[r_id]["mskuFinallInboundDate"]=line.mskuInboundDate
            else:
                msku_info[r_id]["mskuFinallInboundDate"] = max([msku_info[r_id]["mskuFinallInboundDate"] ,line.mskuInboundDate])

    for r_id, v in msku_fee.items():
        msku_info[r_id]['mskuAvgFee'] = sum(v) / len(v) if v else 0
        msku_info[r_id]['mskuTotalFee'] = sum(v)
    for r_id, v in msku_head_fee.items():
        msku_info[r_id]['mskuAvgHeadFee'] = sum(v) / len(v) if v else 0
        msku_info[r_id]['mskuTotalHeadFee'] = sum(v)
    for r_id, v in msku_buy_and_head_fee.items():
        msku_info[r_id]['mskuAvgBuyAndHeadFee'] = sum(v) / len(v) if v else 0
        msku_info[r_id]['mskuTotalBuyAndHeadFee'] = sum(v)

    for r_id, v in msku_msku_batch_number.items():
        msku_info[r_id]['mskuSendTimes'] = len(v)
    # for r_id,v in msku_info.items():
    #     msku_info[r_id]["mskuLeft"] = v["mskuTotalSent"]-v["mskuHasPurchased"]
    to_mongo(m=MskuInventoryIndex, datas=list(msku_info.values()), filters=["campanyId","whId", "ean"])


def main():
    MskuInventoryIndex.objects().count()
    MskuInventoryDetail.objects().count()
    data = old_msku_inventory_detail_model.objects()
    ups = []
    for obj in data:
        ups.append({
            "campanyId": CAMPANY_ID,
            "whId": obj.msku_wh_id,
            "ean": obj.ean,
            "mskuBatchNumber": obj.msku_batch_number,
            "mskuBatchOrder": obj.msku_batch_order,
            "mskuFee": obj.msku_fee,
            "mskuHeadFee": obj.msku_head_fee,
            "mskuBuyAndHeadFee": obj.msku_buy_and_head_fee,
            "mskuInboundDate": obj.msku_inbound_date,
            "skusInfo": [{
                "whId": s.get("sku_wh_id", None),
                "sku": s.get("sku", None),
                "skuBatchNumber": s.get("sku_batch_number", None),
                "skuBatchOrder": s.get("sku_batch_order", None),
                "skuFee": s.get("sku_fee", None),
            } for s in obj.skus_info],
            "status": obj.status,
            "buyCountry": obj.buy_country,
            "orderId": obj.order_id,
            "statusVersion": obj.status_version,
            "tip": "",
            "deleted": obj.deleted
        })
        for s in obj.skus_info:
            SkuInventoryDetail.objects(**{
                "campanyId":CAMPANY_ID,
                "whId": s.get("sku_wh_id", None),
                "sku": s.get("sku", None),
                "skuBatchNumber": s.get("sku_batch_number", None),
                "skuBatchOrder": s.get("sku_batch_order", None),
            }).update(skuStatus=3,toEan=obj.ean,toMskuBatchNumber=obj.msku_batch_number,toMskuBatchOrder=obj.msku_batch_order)
    to_mongo(MskuInventoryDetail, ups, ["campanyId","whId", "ean", "mskuBatchNumber", "mskuBatchOrder"])
    refresh_msku_index_data()


if __name__ == '__main__':
    connect(host="mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin", alias='new_db')
    old_msku_inventory_index_model = ModelManager.get_model("msku_inventory_index", "base")
    old_msku_inventory_detail_model = ModelManager.get_model("msku_inventory_detail", "base")
    refresh_msku_index_data()
    # main()
    # objs = MskuInventoryDetail.objects().only("mskuBatchNumber","skusInfo")
    # for obj in objs:
    #     if obj.mskuBatchNumber and obj.mskuBatchNumber<20251212:
    #         skusInfo = obj.skusInfo
    #         for i in skusInfo:
    #             i["skuBatchNumber"] = int_to_timestamp(i["skuBatchNumber"])
    #         obj.update(skusInfo=skusInfo)