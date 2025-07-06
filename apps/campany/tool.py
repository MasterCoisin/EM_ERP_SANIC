# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：tool.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-02-11 16:53 
-------------------------------------
'''
import datetime
import time

from motor.motor_asyncio import AsyncIOMotorCollection
from sanic import Sanic

from config.constant import APP_NAME
from utils.common import get_uuid

app = Sanic.get_app(APP_NAME)


async def get_campany_info_by_id(campanyId):
    collection: AsyncIOMotorCollection = app.ctx.mongo["campany"]
    result = await collection.find_one({"campanyId": campanyId}, {"_id": 0})
    return result


async def get_campany_is_vip(campanyId):
    collection: AsyncIOMotorCollection = app.ctx.mongo["campany"]
    result = await collection.find_one({"campanyId": campanyId}, {"_id": 0, "isVip": 1,"isSvip":1,"isSuper":1, "expireTime": 1})
    if result.get("isVip", False) and (
            result.get("expireTime", 0) is None or result.get("expireTime", 0) < time.time()):
        await collection.update_one({"campanyId": campanyId}, {"$set": {"isVip": False,"isSvip": False, "expireTime": None}})
        return False,False,False
    return result.get("isVip", False),result.get("isSvip", False),result.get("isSuper", False)


async def get_campany_info_by_name(campanyName):
    collection: AsyncIOMotorCollection = app.ctx.mongo["campany"]
    result = await collection.find_one({"campanyName": campanyName}, {"_id": 0})
    return result


async def create_campany_info(campanyName):
    collection: AsyncIOMotorCollection = app.ctx.mongo["campany"]
    result = await collection.insert_one({"campanyId": get_uuid(), "campanyName": campanyName, "expireTime": None,
                                          "isVip": False,"isSvip":False})
    return await get_campany_info_by_name(campanyName=campanyName)


async def init_campany_data(campany_id):
    # 节日初始化
    collection_festival: AsyncIOMotorCollection = app.ctx.mongo["festival"]
    if not await collection_festival.find_one({"campanyId": campany_id, "festival_code": "nn"}, {"_id": 0}):
        await collection_festival.insert_one({"campanyId": campany_id, "festival_code": "nn",
                                              "deleted": False,
                                              "festival_name": "无",
                                              "updateTime": datetime.datetime.now()})
    # 打印模板初始化
    collection_print_template: AsyncIOMotorCollection = app.ctx.mongo["print_template"]
    await collection_print_template.insert_one({
        "name": "默认模板",
        "template": {
            "panels": [
                {
                    "index": 0,
                    "name": 1,
                    "height": 100,
                    "width": 100,
                    "paperHeader": 0,
                    "paperFooter": 283.464566929134,
                    "printElements": [
                        {
                            "options": {
                                "left": 126,
                                "top": 124.5,
                                "height": 36,
                                "width": 43.5,
                                "right": 168.980751624474,
                                "bottom": 161.076920435979,
                                "vCenter": 147.230751624474,
                                "hCenter": 143.076920435979,
                                "field": "ce",
                                "src": "https://www.fzwala.com/api/images/get/1ffcc24d-19cd-11f0-87d3-70d823b40eb9",
                                "fit": "contain",
                                "coordinateSync": False,
                                "widthHeightSync": False
                            },
                            "printElementType": {
                                "title": "图片",
                                "type": "image"
                            }
                        },
                        {
                            "options": {
                                "left": 210,
                                "top": 126,
                                "height": 36,
                                "width": 37.5,
                                "field": "0_3_ban",
                                "src": "https://www.fzwala.com/api/images/get/6cf4747f-19cd-11f0-8ffc-70d823b40eb9",
                                "fit": "contain",
                                "coordinateSync": False,
                                "widthHeightSync": False,
                                "showInPage": "none",
                                "right": 246.865381094126,
                                "bottom": 161.653843512902,
                                "vCenter": 228.115381094126,
                                "hCenter": 143.653843512902
                            },
                            "printElementType": {
                                "title": "图片",
                                "type": "image"
                            }
                        },
                        {
                            "options": {
                                "left": 6,
                                "top": 4.5,
                                "height": 270,
                                "width": 270,
                                "right": 275.906238555908,
                                "bottom": 274.968752861023,
                                "vCenter": 140.906238555908,
                                "hCenter": 139.968752861023,
                                "coordinateSync": False,
                                "widthHeightSync": False
                            },
                            "printElementType": {
                                "title": "矩形",
                                "type": "rect"
                            }
                        },
                        {
                            "options": {
                                "left": 75,
                                "top": 6,
                                "height": 9.75,
                                "width": 196.5,
                                "title": "Name",
                                "field": "eu_name",
                                "coordinateSync": False,
                                "widthHeightSync": False,
                                "fontSize": 6,
                                "fontWeight": "bold",
                                "qrCodeLevel": 0,
                                "right": 271.5,
                                "bottom": 15.7500014305115,
                                "vCenter": 173.25,
                                "hCenter": 10.8750014305115,
                                "testData": "欧代名称"
                            },
                            "printElementType": {
                                "title": "文本",
                                "type": "text"
                            }
                        },
                        {
                            "options": {
                                "left": 10.5,
                                "top": 15,
                                "height": 27,
                                "width": 57,
                                "src": "https://www.fzwala.com/api/images/get/d44fb7c2-1909-11f0-8e6a-70d823b40eb9",
                                "fit": "contain",
                                "coordinateSync": False,
                                "widthHeightSync": False,
                                "right": 67.2187442779541,
                                "bottom": 37.9687471389771,
                                "vCenter": 38.7187442779541,
                                "hCenter": 24.4687471389771
                            },
                            "printElementType": {
                                "title": "图片",
                                "type": "image"
                            }
                        },
                        {
                            "options": {
                                "left": 75,
                                "top": 16.5,
                                "height": 9.75,
                                "width": 196.5,
                                "title": "Email",
                                "field": "eu_email",
                                "coordinateSync": False,
                                "widthHeightSync": False,
                                "fontSize": 6,
                                "fontWeight": "bold",
                                "qrCodeLevel": 0,
                                "right": 270.714849472046,
                                "bottom": 26.68359375,
                                "vCenter": 172.464849472046,
                                "hCenter": 21.80859375,
                                "qid": "eu_1",
                                "testData": "欧代邮箱"
                            },
                            "printElementType": {
                                "title": "文本",
                                "type": "text"
                            }
                        },
                        {
                            "options": {
                                "left": 75,
                                "top": 27,
                                "height": 21,
                                "width": 196.5,
                                "title": "Address",
                                "field": "eu_address",
                                "coordinateSync": False,
                                "widthHeightSync": False,
                                "fontSize": 6,
                                "fontWeight": "bold",
                                "qrCodeLevel": 0,
                                "right": 273.527349472046,
                                "bottom": 36.2460908889771,
                                "vCenter": 175.277349472046,
                                "hCenter": 31.3710908889771,
                                "qid": "eu_2",
                                "testData": "欧代地址",
                                "lineHeight": 6.75
                            },
                            "printElementType": {
                                "title": "文本",
                                "type": "text"
                            }
                        },
                        {
                            "options": {
                                "left": 6,
                                "top": 50,
                                "height": 4,
                                "width": 270,
                                "borderWidth": "0.75",
                                "right": 95.9999942779541,
                                "bottom": 52.5000085830688,
                                "vCenter": 50.9999942779541,
                                "hCenter": 48.0000085830688,
                                "coordinateSync": False,
                                "widthHeightSync": False
                            },
                            "printElementType": {
                                "title": "横线",
                                "type": "hline"
                            }
                        },
                        {
                            "options": {
                                "left": 9,
                                "top": 52.5,
                                "height": 15,
                                "width": 262.5,
                                "title": "Manufacturer",
                                "field": "manufacturer_name",
                                "testData": "公司名称",
                                "coordinateSync": False,
                                "widthHeightSync": False,
                                "fontSize": 6,
                                "fontWeight": "bold",
                                "textAlign": "left",
                                "lineHeight": 6.75,
                                "right": 159.176478666418,
                                "bottom": 96.0000107709099,
                                "vCenter": 84.1764786664177,
                                "hCenter": 75.0000107709099
                            },
                            "printElementType": {
                                "title": "长文",
                                "type": "longText"
                            }
                        },
                        {
                            "options": {
                                "left": 6,
                                "top": 69,
                                "height": 9,
                                "width": 270,
                                "borderWidth": 0.75
                            },
                            "printElementType": {
                                "title": "横线",
                                "type": "hline"
                            }
                        },
                        {
                            "options": {
                                "left": 9,
                                "top": 70.5,
                                "height": 15,
                                "width": 130,
                                "title": "Manufacturer E-mail",
                                "field": "manufacturer_email",
                                "testData": "公司邮箱",
                                "coordinateSync": False,
                                "widthHeightSync": False,
                                "fontSize": 6,
                                "fontWeight": "bold",
                                "textAlign": "left",
                                "lineHeight": 6.75,
                                "right": 266.906247138977,
                                "bottom": 85.4999971389771,
                                "vCenter": 135.656247138977,
                                "hCenter": 77.9999971389771,
                                "qid": "manufacturer_1"
                            },
                            "printElementType": {
                                "title": "长文",
                                "type": "longText"
                            }
                        },
                        {
                            "options": {
                                "left": 141,
                                "top": 70.5,
                                "height": 15,
                                "width": 130,
                                "title": "Batch Number",
                                "field": "batch_number",
                                "testData": "755113558565-202411",
                                "coordinateSync": False,
                                "widthHeightSync": False,
                                "fontSize": 6,
                                "fontWeight": "bold",
                                "textAlign": "left",
                                "lineHeight": 6.75,
                                "right": 269.464840888977,
                                "bottom": 87.0585966110229,
                                "vCenter": 204.464840888977,
                                "hCenter": 79.5585966110229,
                                "qid": "manufacturer_2"
                            },
                            "printElementType": {
                                "title": "长文",
                                "type": "longText"
                            }
                        },
                        {
                            "options": {
                                "left": 6,
                                "top": 87,
                                "height": 2,
                                "width": 270,
                                "borderWidth": "0.75",
                                "coordinateSync": False,
                                "widthHeightSync": False
                            },
                            "printElementType": {
                                "title": "横线",
                                "type": "hline"
                            }
                        },
                        {
                            "options": {
                                "left": 9,
                                "top": 89,
                                "height": 15,
                                "width": 262.5,
                                "title": "Manufacturer Address",
                                "field": "manufacturer_address",
                                "testData": "公司地址",
                                "coordinateSync": False,
                                "widthHeightSync": False,
                                "fontSize": 6,
                                "fontWeight": "bold",
                                "textAlign": "left",
                                "lineHeight": 6.75,
                                "right": 269.777340888977,
                                "bottom": 106.089849472046,
                                "vCenter": 138.527340888977,
                                "hCenter": 98.5898494720459,
                                "qid": "manufacturer_2"
                            },
                            "printElementType": {
                                "title": "长文",
                                "type": "longText"
                            }
                        },
                        {
                            "options": {
                                "left": 6,
                                "top": 105,
                                "height": 2,
                                "width": 270,
                                "borderWidth": "0.75",
                                "coordinateSync": False,
                                "widthHeightSync": False
                            },
                            "printElementType": {
                                "title": "横线",
                                "type": "hline"
                            }
                        },
                        {
                            "options": {
                                "left": 9,
                                "top": 106.5,
                                "height": 15,
                                "width": 263,
                                "title": "Product Name",
                                "field": "product_name",
                                "testData": "产品三国语言名称",
                                "coordinateSync": False,
                                "widthHeightSync": False,
                                "fontSize": 6,
                                "fontWeight": "bolder",
                                "textAlign": "left",
                                "lineHeight": 6.75,
                                "right": 270.714840888977,
                                "bottom": 124.781255722046,
                                "vCenter": 139.464840888977,
                                "hCenter": 117.281255722046,
                                "qid": "manufacturer_3"
                            },
                            "printElementType": {
                                "title": "长文",
                                "type": "longText"
                            }
                        },
                        {
                            "options": {
                                "left": 6,
                                "top": 124.5,
                                "height": 9,
                                "width": 270,
                                "borderWidth": 0.75,
                                "right": 94.875,
                                "bottom": 133.124997138977,
                                "vCenter": 49.875,
                                "hCenter": 128.624997138977
                            },
                            "printElementType": {
                                "title": "横线",
                                "type": "hline"
                            }
                        },
                        {
                            "options": {
                                "left": 10.5,
                                "top": 129,
                                "height": 60,
                                "width": 60,
                                "title": "二维码",
                                "qrcodeType": "qrcode",
                                "testData": "https://walawaladocs.de/?ean=755113559012",
                                "field": "docs_url",
                                "qrCodeLevel": 0,
                                "coordinateSync": False,
                                "widthHeightSync": False,
                                "right": 70.125,
                                "bottom": 188.249997138977,
                                "vCenter": 40.125,
                                "hCenter": 158.249997138977,
                                "hideTitle": True
                            },
                            "printElementType": {
                                "title": "二维码",
                                "type": "qrcode"
                            }
                        },
                        {
                            "options": {
                                "left": 75,
                                "top": 138,
                                "height": 42,
                                "width": 33,
                                "title": "Product Description\nscan the QR code to view",
                                "coordinateSync": False,
                                "widthHeightSync": False,
                                "fontSize": 6,
                                "fontWeight": "bolder",
                                "lineHeight": 6.75,
                                "right": 107.999988555908,
                                "bottom": 180.749982833862,
                                "vCenter": 91.4999885559082,
                                "hCenter": 159.749982833862
                            },
                            "printElementType": {
                                "title": "长文",
                                "type": "longText"
                            }
                        },
                        {
                            "options": {
                                "left": 112.5,
                                "top": 156,
                                "height": 34.5,
                                "width": 159,
                                "title": "条形码",
                                "barcodeType": "code128",
                                "testData": "755113551111",
                                "right": 270.999994913737,
                                "bottom": 190.083321253459,
                                "vCenter": 191.499994913737,
                                "hCenter": 172.833321253459,
                                "field": "ean",
                                "coordinateSync": False,
                                "widthHeightSync": False,
                                "fontWeight": "bold",
                                "letterSpacing": 0.75,
                                "lineHeight": 6
                            },
                            "printElementType": {
                                "title": "条形码",
                                "type": "barcode"
                            }
                        },
                        {
                            "options": {
                                "left": 6,
                                "top": 193.5,
                                "height": 9,
                                "width": 270,
                                "borderWidth": 0.75
                            },
                            "printElementType": {
                                "title": "横线",
                                "type": "hline"
                            }
                        },
                        {
                            "options": {
                                "left": 9,
                                "top": 195,
                                "height": 76.5,
                                "width": 262.5,
                                "right": 130.999997456868,
                                "bottom": 208.916657129924,
                                "vCenter": 70.9999974568685,
                                "hCenter": 204.041657129924,
                                "field": "warning",
                                "testData": "AVERTISMENT: Pentru a evita riscul de sufocare, țineți ambalajul produsului departe de sugari și copii. ПРЕДУПРЕЖДЕНИЕ: За да избегнете риска от задушаване, дръжте опаковката на продукта далеч от бебета и деца. FIGYELMEZTETÉS: A fulladásveszély elkerülése érdekében tartsa távol a termék csomagolását csecsemőktől és gyermekektől.",
                                "coordinateSync": False,
                                "widthHeightSync": False,
                                "hideTitle": True,
                                "fontSize": 6,
                                "fontWeight": "bold",
                                "lineHeight": 6.75,
                                "qrCodeLevel": 0
                            },
                            "printElementType": {
                                "title": "自定义文本",
                                "type": "text"
                            }
                        }
                    ],
                    "paperNumberLeft": 281,
                    "paperNumberTop": 261,
                    "paperNumberDisabled": True,
                    "paperNumberContinue": True,
                    "orient": 1,
                    "watermarkOptions": {},
                    "panelLayoutOptions": {}
                }
            ]
        },
        "deleted": False,
        "campanyId": campany_id,
        "printTemplateId": get_uuid(),
        "createTime": datetime.datetime.now(),
        "updateTime": datetime.datetime.now(),
    })
