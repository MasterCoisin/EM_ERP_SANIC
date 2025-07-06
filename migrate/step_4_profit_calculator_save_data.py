# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：step_2_profit_calculator_save_data.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：迁移profit_calculator_save_data表
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


class ProfitCalculatorSaveData(DynamicDocument):
    uuid = StringField()
    shop = StringField() #
    productName = StringField()#
    url1688 = StringField()#
    images = ListField() #
    tip = StringField()
    competitorUrls = StringField()
    length = FloatField()#
    width = FloatField()#
    height = FloatField()#
    weight = FloatField()#
    volumeWeight: FloatField()#
    weighing: FloatField()#
    purchaseCost = FloatField()#
    commission = FloatField()#
    soldPriceWithVat = FloatField()#
    soldPriceWithoutVat = FloatField()#
    # invoiceTaxPoint = FloatField(default=0)
    logisticsPerKgCostTielu = FloatField(default=20)
    logisticsCostPerKgElseTielu = FloatField(default=2)
    logisticsCostPerKgAirport = FloatField(default=65)
    logisticsCostPerKgElseAirport = FloatField(default=0)
    logisticsCostTielu = FloatField()#
    logisticsCostAirport = FloatField()#
    fbeFee = FloatField()#
    profitRonTielu = FloatField()#
    profitRmbTielu = FloatField()#
    profitRateTielu = FloatField()#
    profitRonAirport = FloatField()  #
    profitRmbAirport = FloatField()  #
    profitRateAirport = FloatField()  #
    costProfitMarginTielu = FloatField(help_text="成本利润率")#
    costProfitMarginAirport = FloatField(help_text="成本利润率")  #

    hasToSku = BooleanField()
    createTime = DateTimeField(default=datetime.datetime.now)
    updateTime = DateTimeField(default=datetime.datetime.now)
    deleted = BooleanField(default=False)
    meta = {
        'db_alias': 'new_db',
        'collection': 'profit_calculator_save_data',
        "indexes": [
            {
                'fields': ['createTime'],
                "name": "createTime"
            }
        ]
    }


def main():
    ProfitCalculatorSaveData.objects().count()
    data = old_profit_calculator_save_data_model.objects()
    ups = []
    for obj in data:
        ups.append({
            "campanyId": CAMPANY_ID,
            "uuid": get_uuid(),
            "shop": obj.product_profit_cal_data.get("shop", None),
            "productName": obj.product_profit_cal_data.get("product_name", None),
            "url1688": obj.product_profit_cal_data.get("url_1688", None),
            "images": obj.info_1688.get("images", []),
            "tip": obj.product_profit_cal_data.get("tip", None),
            "competitorUrls": obj.product_profit_cal_data.get("competitors_url", None),
            "length": str_to_float(obj.product_profit_cal_data.get("length", None)),
            "width": str_to_float(obj.product_profit_cal_data.get("width", None)),
            "height": str_to_float(obj.product_profit_cal_data.get("height", None)),
            "weight": str_to_float(obj.product_profit_cal_data.get("weight", None)),
            "volumeWeight": str_to_float(obj.cal_result.get("volume_weight", None)),
            "weighing": str_to_float(obj.cal_result.get("weighing", None)),
            "purchaseCost": str_to_float(obj.product_profit_cal_data.get("purchase_cost", None)),
            "commission": str_to_float(obj.product_profit_cal_data.get("commission", None)),
            "soldPriceWithoutVat": str_to_float(
                obj.product_profit_cal_data.get("sold_price", None)) / 1.19 if str_to_float(
                obj.product_profit_cal_data.get("sold_price", None)) else None,
            "soldPriceWithVat": str_to_float(obj.product_profit_cal_data.get("sold_price", None)),
            # "invoiceTaxPoint": str_to_float(obj.product_profit_cal_data.get("invoice_tax_point", None)),
            "hasToSku": obj.sku_info.get("has_use", False),
            "logisticsPerKgCostTielu": 20,
            "logisticsCostPerKgElseTielu": 0,
            "logisticsCostPerKgAirport": 60,
            "logisticsCostPerKgElseAirport": 0,
            "logisticsCostTielu": None,
            "logisticsCostAirport": None,
            "fbeFeeRon": None,
            "fbeFeeRmb": None,
            "profitRonTielu": None,
            "profitRmbTielu": None,
            "profitRateTielu": None,
            "costProfitMarginTielu": None,
            "profitRonAirport": None,
            "profitRmbAirport": None,
            "profitRateAirport": None,
            "costProfitMarginAirport": None,
            "createTime": datetime.datetime.fromtimestamp(obj.create_time),
            "updateTime": datetime.datetime.fromtimestamp(obj.create_time),
            "deleted": obj.is_deleted
        })
    to_mongo(ProfitCalculatorSaveData, ups, ["campanyId","uuid"])


if __name__ == '__main__':
    connect(host="mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin", alias='new_db')
    old_profit_calculator_save_data_model = ModelManager.get_model("profit_calculator_save_data", "base")
    main()
