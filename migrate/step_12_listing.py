# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：step_7_listing.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：迁移listing表
@Date        ：2024-12-19 21:16 
-------------------------------------
'''
import datetime
import json
import time

from loguru import logger
from mongoengine import *

from migrate.constant import CAMPANY_ID
from utils.common import to_mongo, to_float
from utils.models import ModelManagerOld as ModelManager


class Listing(DynamicDocument):
    campanyId = StringField()
    shop = StringField()

    ean = StringField()
    listingName = StringField()
    url1688 = StringField()
    images = ListField()
    tip = StringField()
    baseInfo = DictField()
    emAttribute = DictField()
    logisticsAttributes = DictField()
    flag = DictField()
    invoiceInfo = DictField()
    gprs = DictField()
    addFee = DictField()
    skuList = ListField()
    packingList = ListField()
    emSaleInfo = DictField()
    createTime = DateTimeField(default=datetime.datetime.now)
    updateTime = DateTimeField(default=datetime.datetime.now)
    deleted = BooleanField(default=False)
    meta = {
        'db_alias': 'new_db',
        'collection': 'listing',
        "indexes": [
            {
                'fields': ['ean'],
                "name": "ean"
            },
            {
                'fields': ['msku'],
                "name": "msku"
            },
            {
                'fields': ['createTime'],
                "name": "createTime"
            }
        ]
    }


def main():
    Listing.objects().count()
    data = old_listing_model.objects(deleted=False)
    ups = []
    for obj in data:
        ups.append({
            "campanyId": CAMPANY_ID,
            "shop": obj.base_info.get("shop", None),
            "ean": obj.base_info.get("ean", None),
            "msku": obj.base_info.get("msku", None),
            "listingName": obj.base_info.get("listing_name", None),
            "images": [i["url"].split("/")[-1] for i in obj.base_info.get("images", [])],
            "baseInfo": {
                "firstCreateDate": str(obj.base_info.get("first_create_date", None))[:10],
                "specialFestival": obj.base_info.get("special_festival", None),
            },
            "emAttribute": {
                "id": {
                    "ro": None,
                    "bg": None,
                    "hu": None
                },
                "brand": {
                    "ro": obj.base_info.get("em_attribute", {}).get("brand", None),
                    "bg": "",
                    "hu": "",
                },
                "category": {
                    "ro": obj.base_info.get("em_attribute", {}).get("category", None),
                    "bg": None,
                    "hu": None
                },
                "commission": {
                    "ro": obj.base_info.get("em_attribute", {}).get("commission", None),
                    "bg": None,
                    "hu": None
                },
                "html": {
                    "ro": obj.base_info.get("em_attribute", {}).get("html", None),
                    "bg": "",
                    "hu": "",
                },
                "pnk": {
                    "ro": obj.base_info.get("em_attribute", {}).get("pnk", None),
                    "bg": None,
                    "hu": None
                },
                "salePrice": {
                    "ro": to_float(obj.base_info.get("em_attribute", {}).get("sale_price", None)),
                    "bg": None,
                    "hu": None
                },
                "title": {
                    "ro": obj.base_info.get("em_attribute", {}).get("title", None),
                    "bg": "",
                    "hu": "",
                },
                "status": {
                    "ro": None,
                    "bg": None,
                    "hu": None
                }
            },
            "logisticsAttributes": {
                "height": to_float(obj.base_info.get("logistics_attributes", None).get("height", None)),
                "width": to_float(obj.base_info.get("logistics_attributes", None).get("width", None)),
                "length": to_float(obj.base_info.get("logistics_attributes", None).get("length", None)),
                "volumeWeight": to_float(obj.base_info.get("logistics_attributes", None).get("volume_weight", None)),
                "weighing": to_float(obj.base_info.get("logistics_attributes", None).get("weighing", None)),
                "weight": to_float(obj.base_info.get("logistics_attributes", None).get("weight", None)),
            },
            "flag": {
                "isCe": obj.base_info.get("flag", None).get("is_ce", False),
                "isDangerous": obj.base_info.get("flag", None).get("is_dangerous", False),
                "isElectrified": obj.base_info.get("flag", None).get("is_electrified", False),
                "isLiquid": obj.base_info.get("flag", None).get("is_liquid", False),
                "isMagnetized": obj.base_info.get("flag", None).get("is_magnetized", False),
                "isPowder": obj.base_info.get("flag", None).get("is_powder", False),
                "season": obj.base_info.get("flag", None).get("season", None),
                "isBan0To3Age": obj.base_info.get("flag", None).get("is_ban_0_3_age", False),
            },
            "invoiceInfo": {
                "productBrand": obj.base_info.get("invoice_info", {}).get("product_brand", None),
                "productCustomsCode": obj.base_info.get("invoice_info", {}).get("product_customs_code", None),
                "productDeclarationUnitPrice": obj.base_info.get("invoice_info", {}).get(
                    "product_declaration_unit_price", None),
                "productMaterial": obj.base_info.get("invoice_info", {}).get("product_material", None),
                "productModel": obj.base_info.get("invoice_info", {}).get("product_model", None),
                "productNameEn": obj.base_info.get("invoice_info", {}).get("product_name_en", None),
                "productNameZh": obj.base_info.get("invoice_info", {}).get("product_name_zh", None),
                "productUsage": obj.base_info.get("invoice_info", {}).get("product_usage", None),
            },
            "gprs": {
                # "productNameThreeCountryLanguage": obj.base_info.get("product_name_3_country_language", None),
                "warning": obj.base_info.get("warning", None),
                "details": obj.details,
                "laws":[]
            },
            "addFee": obj.base_info.get("add_fee", {}),
            "skuList": [{"sku": sku_info.get("sku", None), "count": sku_info.get("count", None)} for sku_info in
                        obj.sku_list],
            "packingList": [],
            # "profitCalResult": {
            #     "volumeWeight": obj.cal_result.get("volume_weight", None),
            #     "weighing": obj.cal_result.get("weighing", None),
            #     "rejectionError": obj.cal_result.get("rejection_error", None),
            #     "logisticsCostHeadRmb": obj.cal_result.get("logistics_cost_head_rmb", None),
            #     "logisticsCostHeadRon": obj.cal_result.get("logistics_cost_head_ron", None),
            #     "orderFeeRmb": obj.cal_result.get("order_fee_rmb", None),
            #     "orderFeeRon": obj.cal_result.get("order_fee_ron", None),
            #     "profit": obj.cal_result.get("profit", None),
            # },
            # "productProfitCalData": {
            #     "soldPriceWithVat": {"ro": obj.product_profit_cal_data.get("sold_price_with_vat", None), "bg": None,
            #                          "hu": None},
            #     "purchaseCost": {"ro": obj.product_profit_cal_data.get("purchase_cost", None), "bg": None, "hu": None},
            #     "logisticsCostElse": {"ro": obj.product_profit_cal_data.get("logistics_cost_else", None), "bg": None,
            #                           "hu": None},
            # },
            "tip": obj.base_info.get("tip", None),
            "emSaleInfo": {
                "buyButtonRank": {"ro": obj.em_sale_info.get("buy_button_rank", None), "bg": None, "hu": None},
                "stock": {"ro": obj.em_sale_info.get("stock", None), "bg": None, "hu": None},
                "status": {"ro": obj.em_sale_info.get("status", None), "bg": None, "hu": None},
                "ownership": {"ro": obj.em_sale_info.get("ownership", None), "bg": None, "hu": None},
                "bestOfferSalePrice": {"ro": obj.em_sale_info.get("best_offer_sale_price", None), "bg": None,
                                       "hu": None},
                "salePrice": {"ro": to_float(obj.em_sale_info.get("sale_price", None)), "bg": None, "hu": None},
                "currency": {"ro": obj.em_sale_info.get("currency", None), "bg": None, "hu": None},
                "numberOfOffers": {"ro": obj.em_sale_info.get("number_of_offers", None), "bg": None, "hu": None},
                "geniusEligibility": {"ro": obj.em_sale_info.get("genius_eligibility", None), "bg": None, "hu": None},
            },
            "createTime": datetime.datetime.now(),
            "updateTime": datetime.datetime.now(),
            "deleted": obj.deleted
        })
        time.sleep(0.01)
    to_mongo(Listing, ups, ["campanyId","ean"])


if __name__ == '__main__':
    connect(host="mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin", alias='new_db')
    old_listing_model = ModelManager.get_model("listing", "base")
    main()
    # for obj in Listing.objects():
    #     if obj.skuList:
    #         obj.skuList = [{"sku":i["sku"],"count":int(i["count"])} for i in obj.skuList]
    #         obj.update(skuList=obj.skuList)