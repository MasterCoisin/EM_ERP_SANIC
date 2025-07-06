# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：update_listing.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-04-16 16:55 
-------------------------------------
'''
import datetime

import requests

from em_api.estimate import EstimateApi
from migrate.step_13_images import binary_image_to_thumbnail
from utils.common import to_mongo, get_uuid
from utils.models import ModelManager
from loguru import logger
from concurrent.futures import ThreadPoolExecutor

pool = ThreadPoolExecutor(50)
images_model = ModelManager.get_model("images", "base")


def download_img(url,campany_id):
    try:
        obj = images_model.objects(campanyId=campany_id, emUrl=url).only("sourceId").first()
        if not obj:
            payload = {}
            headers = {
                'authority': 'mnks.jxedt.com',
                'accept': '*/*',
                'accept-language': 'zh-CN,zh;q=0.9',
                'cache-control': 'no-cache',
                'cookie': 'id58=CpQQYGVURiFZ60T2B6yZAg==; 58tj_uuid=725838b5-9f4c-481d-941d-4496598cddcc; als=0; Hm_lvt_6be941daec905c6555161e79e92067b2=1700021794; Hm_lvt_e43feb296c32a4add052b7249ed6bf2b=1700021798; Hm_lvt_b54f0f8b3b75a8b7486c9adedf28f361=1700021809; local_car_flag=undefined; jxedt_dialog_time=41879066; carText=%E5%B0%8F%E8%BD%A6; local_city=%E5%85%A8%E5%9B%BD; local_city_pingying=%2F; init_refer=https%253A%252F%252Fwww.baidu.com%252Flink%253Furl%253D1eBygKDDySWxf2p0zdmrWYlNfXZxNTp_Y_EgdGHV_1i%2526wd%253D%2526eqid%253Dc775474200011b580000000665544618; new_uv=3; Hm_lpvt_6be941daec905c6555161e79e92067b2=1700027575; new_session=0; Hm_lpvt_b54f0f8b3b75a8b7486c9adedf28f361=1700027580; Hm_lpvt_e43feb296c32a4add052b7249ed6bf2b=1700027582',
                'pragma': 'no-cache',
                'referer': 'https://mnks.jxedt.com/ckm1/sxlx/',
                'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'x-requested-with': 'XMLHttpRequest'
            }

            response = requests.request("GET", url, headers=headers, data=payload,
                                        proxies={"http": "http://127.0.0.1:10809",
                                                 "https": "http://127.0.0.1:10809"}).content
            uuid_ = get_uuid()
            images_model(campanyId=campany_id,sourceId=uuid_, emUrl=url, sourceImgFile=response,
                         thumbImgFile=binary_image_to_thumbnail(response)).save()
            return uuid_
        return obj.sourceId
    except:
        return url


def update_value(data, key, country, value):
    if key not in data:
        data[key] = {
            "ro": None,
            "bg": None,
            "hu": None
        }
    data[key][country] = value


class ListingUpdater():
    MODEL = ModelManager.get_model("listing", "base")

    def __init__(self, product_baken_data: dict, shop_id, campany_id, country, shop_hash):
        self.product_baken_data: dict = product_baken_data
        self.shop_id = shop_id
        self.campany_id = campany_id
        self.country = country
        self.shop_hash = shop_hash

    def update_listing_data(self, ean, obj):
        part_number_key = self.product_baken_data.get("part_number_key", None)  # PNK
        sale_price = self.product_baken_data.get("sale_price", None)
        category_id = self.product_baken_data.get("category_id", None)
        description = self.product_baken_data.get("description", None)
        title = self.product_baken_data.get("name", None)
        brand = self.product_baken_data.get("brand", None)
        images = self.product_baken_data.get("images", [])
        id_ = self.product_baken_data.get("id", None)
        id_ = id_ if id_ else str(ean)
        #
        images_ = []
        for img in images:
            # pool.submit(download_img,img.get("url", None),self.campany_id)
            uuid_ = download_img(img.get("url", None), self.campany_id)
            if img.get("display_type", 2) == 1:
                images_.insert(0, uuid_)
            else:
                images_.append(uuid_)
        images = images_

        obj.emAttribute["id"][self.country] = id_
        obj.emAttribute["pnk"][self.country] = part_number_key
        obj.emAttribute["salePrice"][self.country] = float(str(sale_price)) if sale_price else sale_price
        obj.emAttribute["category"][self.country] = category_id
        obj.emAttribute["title"][self.country] = title
        obj.emAttribute["html"][self.country] = description
        obj.emAttribute["brand"][self.country] = brand
        if self.country == "ro": obj.images = images

        update_value(obj.emSaleInfo, 'buyButtonRank', self.country,
                     self.product_baken_data.get('buy_button_rank', None))
        update_value(obj.emSaleInfo, 'stock', self.country,
                     self.product_baken_data.get('stock', None)[0].get("value", None))
        update_value(obj.emSaleInfo, 'status', self.country, self.product_baken_data.get('status', None))
        update_value(obj.emSaleInfo, 'ownership', self.country,
                     self.product_baken_data.get('ownership', None))
        update_value(obj.emSaleInfo, 'bestOfferSalePrice', self.country,
                     self.product_baken_data.get('best_offer_sale_price', None))
        update_value(obj.emSaleInfo, 'salePrice', self.country,
                     float(self.product_baken_data.get('sale_price', None)) if self.product_baken_data.get('sale_price',
                                                                                                           None) else self.product_baken_data.get(
                         'sale_price', None))
        update_value(obj.emSaleInfo, 'currency', self.country, self.product_baken_data.get('currency', None))
        update_value(obj.emSaleInfo, 'numberOfOffers', self.country,
                     self.product_baken_data.get('number_of_offers', None))
        update_value(obj.emSaleInfo, 'geniusEligibility', self.country,
                     self.product_baken_data.get('genius_eligibility', None))
        if not obj.emAttribute["commission"][self.country]:
            if self.country == "ro":
                resp = EstimateApi.readSync(id_, shop_hash=self.shop_hash, country=self.country)
                if resp["code"] == 200 and resp.get("data", {}).get("value"):
                    obj.emAttribute["commission"][self.country] = int(float(resp.get("data", {}).get("value")))
                    obj.emAttribute["commission"]["bg"] = int(float(resp.get("data", {}).get("value")))
                    obj.emAttribute["commission"]["hu"] = int(float(resp.get("data", {}).get("value")))
            else:
                if obj.emAttribute["commission"]["ro"]:
                    obj.emAttribute["commission"][self.country] = obj.emAttribute["commission"]["ro"]
        obj.save()
        # logger.info(f"{ean} update success")

    def craete_listing(self, ean):
        part_number_key = self.product_baken_data.get("part_number_key", None)  # PNK
        sale_price = self.product_baken_data.get("sale_price", None)
        category_id = self.product_baken_data.get("category_id", None)
        description = self.product_baken_data.get("description", None)
        title = self.product_baken_data.get("name", None)
        brand = self.product_baken_data.get("brand", None)
        images = self.product_baken_data.get("images", [])
        id_ = self.product_baken_data.get("id", None)
        #
        images_ = []
        for img in images:
            # pool.submit(download_img,img.get("url", None),self.campany_id)
            uuid_ = download_img(img.get("url", None), self.campany_id)
            if img.get("display_type", 2) == 1:
                images_.insert(0, uuid_)
            else:
                images_.append(uuid_)
        images = images_
        new_listing = {
            "ean": ean,
            "addFee": {},
            "baseInfo": {
                "firstCreateDate": "",
                "specialFestival": ""
            },
            "emAttribute": {
                "id": {
                    "ro": None,
                    "bg": None,
                    "hu": None
                },
                "brand": {
                    "ro": "OEM",
                    "bg": "OEM",
                    "hu": "OEM"
                },
                "category": {
                    "ro": None,
                    "bg": None,
                    "hu": None
                },
                "commission": {
                    "ro": None,
                    "bg": None,
                    "hu": None
                },
                "html": {
                    "ro": "",
                    "bg": "",
                    "hu": ""
                },
                "pnk": {
                    "ro": "",
                    "bg": "",
                    "hu": ""
                },
                "salePrice": {
                    "ro": None,
                    "bg": None,
                    "hu": None
                },
                "title": {
                    "ro": "",
                    "bg": "",
                    "hu": ""
                }
            },
            "emSaleInfo": {
                "buyButtonRank": {
                    "ro": None,
                    "bg": None,
                    "hu": None
                },
                "stock": {
                    "ro": None,
                    "bg": None,
                    "hu": None
                },
                "status": {
                    "ro": None,
                    "bg": None,
                    "hu": None
                },
                "ownership": {
                    "ro": None,
                    "bg": None,
                    "hu": None
                },
                "bestOfferSalePrice": {
                    "ro": None,
                    "bg": None,
                    "hu": None
                },
                "salePrice": {
                    "ro": None,
                    "bg": None,
                    "hu": None
                },
                "currency": {
                    "ro": None,
                    "bg": None,
                    "hu": None
                },
                "numberOfOffers": {
                    "ro": None,
                    "bg": None,
                    "hu": None
                },
                "geniusEligibility": {
                    "ro": None,
                    "bg": None,
                    "hu": None
                }
            },
            "flag": {
                "isCe": False,
                "isDangerous": False,
                "isElectrified": False,
                "isLiquid": False,
                "isMagnetized": False,
                "isPowder": False,
                "season": None,
                "isBan0To3Age": False
            },
            "gprs": {
                "warning": "",
                "details": [],
                "laws": []
            },
            "images": [
            ],
            "invoiceInfo": {
                "productBrand": "无",
                "productCustomsCode": "",
                "productDeclarationUnitPrice": None,
                "productMaterial": "",
                "productModel": "无",
                "productNameEn": "",
                "productNameZh": "",
                "productNameRo": "",
                "productNameBg": "",
                "productNameHu": "",
                "productUsage": ""
            },
            "listingName": "",
            "logisticsAttributes": {
                "height": None,
                "width": None,
                "length": None,
                "volumeWeight": None,
                "weighing": None,
                "weight": None
            },
            "msku": None,
            "packingList": [],
            "shop": self.shop_id,
            "skuList": [
            ],
            "tip": "",
            "competitorUrls": [],
            "campanyId": self.campany_id,
            "createTime": datetime.datetime.now(),
            "updateTime": datetime.datetime.now(),
            "listingNameEn": None,
            "deleted": False
        }

        new_listing["emAttribute"]["pnk"][self.country] = part_number_key
        new_listing["emAttribute"]["salePrice"][self.country] = sale_price
        new_listing["emAttribute"]["category"][self.country] = category_id
        new_listing["emAttribute"]["title"][self.country] = title
        new_listing["emAttribute"]["html"][self.country] = description
        new_listing["emAttribute"]["brand"][self.country] = brand
        new_listing["emAttribute"]["id"][self.country] = id_
        if self.country == "ro":
            new_listing["images"] = images

        update_value(new_listing["emSaleInfo"], 'buyButtonRank', self.country,
                     self.product_baken_data.get('buy_button_rank', None))
        update_value(new_listing["emSaleInfo"], 'stock', self.country,
                     self.product_baken_data.get('stock', None)[0].get("value", None))
        update_value(new_listing["emSaleInfo"], 'status', self.country, self.product_baken_data.get('status', None))
        update_value(new_listing["emSaleInfo"], 'ownership', self.country,
                     self.product_baken_data.get('ownership', None))
        update_value(new_listing["emSaleInfo"], 'bestOfferSalePrice', self.country,
                     self.product_baken_data.get('best_offer_sale_price', None))
        update_value(new_listing["emSaleInfo"], 'salePrice', self.country,
                     float(self.product_baken_data.get('sale_price', None)) if self.product_baken_data.get('sale_price',
                                                                                                           None) else self.product_baken_data.get(
                         'sale_price', None))
        update_value(new_listing["emSaleInfo"], 'currency', self.country, self.product_baken_data.get('currency', None))
        update_value(new_listing["emSaleInfo"], 'numberOfOffers', self.country,
                     self.product_baken_data.get('number_of_offers', None))
        update_value(new_listing["emSaleInfo"], 'geniusEligibility', self.country,
                     self.product_baken_data.get('genius_eligibility', None))
        if self.country == "ro":
            resp = EstimateApi.readSync(ean, shop_hash=self.shop_hash, country=self.country)
            if resp["code"] == 200 and resp.get("data", {}).get("value"):
                new_listing["emAttribute"]["commission"][self.country] = int(float(resp.get("data", {}).get("value")))
                new_listing["emAttribute"]["commission"]["bg"] = int(float(resp.get("data", {}).get("value")))
                new_listing["emAttribute"]["commission"]["hu"] = int(float(resp.get("data", {}).get("value")))

        to_mongo(self.MODEL, [new_listing], ["campanyId", "shop", "ean", "deleted"])
        logger.info(f"{ean} create success")

    def update(self):
        try:
            ean = self.product_baken_data.get("ean", [])[0] if self.product_baken_data.get("ean", []) else None
            obj = self.MODEL.objects(shop=self.shop_id, campanyId=self.campany_id, ean=ean).first()
            if obj:
                self.update_listing_data(ean, obj)
            else:
                self.craete_listing(ean)
        except Exception as e:
            logger.exception(e)
