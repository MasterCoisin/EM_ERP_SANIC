# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BACKEN 
@File        ：api_1688_tool.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024-05-07 16:25 
-------------------------------------
'''
from aop.api import AlibabaTradeReceiveAddressGetParam, AlibabaTradeFastCreateOrderParam, AlibabaAlipayUrlGetParam, \
    AlibabaTradeGetBuyerViewParam
import aop

# connect(host="mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin", alias='new_db')





class Api1688():
    APP_KEY = 3318329
    APP_SECRET = "lRglLuOzbHk"
    # TOKEN = "bd510fb6-4dfa-442b-8cf0-1fbd0fb42576"
    aop.set_default_server('gw.open.1688.com')
    aop.set_default_appinfo(APP_KEY, APP_SECRET)
    ADDRESS_INFO = {}  # []

    @classmethod
    def get_address(cls, shop_id, token,campany_id):
        req = AlibabaTradeReceiveAddressGetParam()
        req.access_token = token  # cls.TOKEN
        try:
            resp = req.get_response()
            add = resp.get("result", {}).get("receiveAddressItems", [])
            for i in add:
                i["label"] = i.get("addressCodeText", "") + " " + i.get("townName", "") + i.get("address",
                                                                                                "") + " 收货人:" + i.get(
                    "fullName", "") + " 手机号:" + i.get("mobilePhone", "") + " "
            print(add)
            if campany_id not in cls.ADDRESS_INFO:
                cls.ADDRESS_INFO[campany_id] = {}
            cls.ADDRESS_INFO[campany_id][shop_id] = add
        except aop.ApiError as e:
            print(e)
            pass  # log
        except aop.AopError as e:
            print(e)
            pass  # log
        except Exception as e:
            print(e)
            pass  # log

    @classmethod
    def create_order(cls, address_id, skus_data, tip_for_seller, token):
        req = AlibabaTradeFastCreateOrderParam()
        req.access_token = token  # cls.TOKEN
        req.flow = "general"
        req.message = tip_for_seller
        req.addressParam = str({"addressId": address_id})
        req.cargoParamList = str(
            [{"specId": i["specId"]["specId"], "quantity": i["count"], "offerId": int(i["offerId"])} for i in skus_data])
        try:
            resp = req.get_response()
            return resp
        except aop.ApiError as e:
            print(1, e)
            return {}
        except aop.AopError as e:
            print(2, e)
            return {}
        except Exception as e:
            print(3, e)
            return {}

    @classmethod
    def get_alipay_url(cls, order_id, token):
        req = AlibabaAlipayUrlGetParam()
        req.access_token = token  # cls.TOKEN
        req.orderIdList = str([order_id])
        try:
            resp = req.get_response()
            return resp
        except aop.ApiError as e:
            print(1, e)
            return {}
        except aop.AopError as e:
            print(2, e)
            return {}
        except Exception as e:
            print(3, e)
            return {}

    @classmethod
    def get_order_info(cls, order_id, token):
        req = AlibabaTradeGetBuyerViewParam()
        req.access_token = token  # cls.TOKEN
        req.webSite = "1688"
        req.orderId = int(order_id)
        try:
            resp = req.get_response()
            return resp
        except aop.ApiError as e:
            print(1, e)
            return {}
        except aop.AopError as e:
            print(2, e)
            return {}
        except Exception as e:
            print(3, e)
            return {}


# for shop_obj in ShopManager.objects(deleted=False).only("shop_id", "token1688"):
#     Api1688.get_address(shop_id=shop_obj.shop_id, token=shop_obj.token1688)
# print(Api1688.get_order_info("3892646630858752004"))
