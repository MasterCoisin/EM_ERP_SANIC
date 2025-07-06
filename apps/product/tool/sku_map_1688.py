# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BACKEN 
@File        ：sku_map_1688.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024-05-06 15:03 
-------------------------------------
'''
import json
import re

import aiohttp
from retrying import retry

from models.supplier import Supplier
from utils.common import get_1688_product_id, get_uuid
from sanic import Sanic
from config.constant import APP_NAME
from loguru import logger

app = Sanic.get_app(APP_NAME)


class SkuMap1688Old():
    @classmethod
    @retry(stop_max_attempt_number=3, wait_random_min=100, wait_random_max=1000)
    async def get_html(cls, url):
        logger.info(url)
        payload = {}
        headers = {
  'AK-Client-Type': 'web',
  'AK-Origin': 'https://erp.lingxing.com',
  'Accept': 'application/json, text/plain, */*',
  'Accept-Language': 'zh-CN,zh;q=0.9',
  'Cache-Control': 'no-cache',
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Referer': 'https://erp.lingxing.com/erp/pairingManage',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
  'X-AK-Company-Id': '901556342054979072',
  'X-AK-ENV-KEY': 'SAAS-130',
  'X-AK-Language': 'zh',
  'X-AK-PLATFORM': '1',
  'X-AK-Request-Id': 'b2f5a4f8-5b39-44c8-8b10-88df65934cd5',
  'X-AK-Request-Source': 'erp',
  'X-AK-Uid': '10764951',
  'X-AK-Version': '3.5.8.3.0.078',
  'X-AK-Zid': '10764951',
  'auth-token': '75500/GIOSREd+QE6Pn/xuHpLf9PZMDrW9fFnVypvWMNfR0xs9wzjYD6VZUqaggVvYGVsKbNCbw3npylGZ1ImZtAC8lB4fsGU0JDoIaEv6OLuXBw/KQ6RsakwRGOlMsPLdvVkZAewc1ra5DZZ5X5VW+oWYhJjP61b9Hx8rg',
  'sec-ch-ua': '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'Cookie': 'sajssdk_2015_cross_new_user=1; __wpkreporterwid_=e1c87c96-ba05-4e5d-37f3-04c0543bf9a8; Hm_lvt_e1b07b01489084694814b73e755122ea=1744706009; HMACCOUNT=4A5652E1F294C8BF; _gcl_au=1.1.2079565331.1744706009; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2210764951-10764951%22%2C%22first_id%22%3A%221963894f3a23349-07a18dcd02bd358-4c657b58-2073600-1963894f3a3357e%22%2C%22props%22%3A%7B%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTk2Mzg5NGYzYTIzMzQ5LTA3YTE4ZGNkMDJiZDM1OC00YzY1N2I1OC0yMDczNjAwLTE5NjM4OTRmM2EzMzU3ZSIsIiRpZGVudGl0eV9sb2dpbl9pZCI6IjEwNzY0OTUxLTEwNzY0OTUxIn0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%2210764951-10764951%22%7D%2C%22%24device_id%22%3A%221963894f3a23349-07a18dcd02bd358-4c657b58-2073600-1963894f3a3357e%22%7D; company_id=901556342054979072; envKey=SAAS-130; env_key=SAAS-130; authToken=75500%2FGIOSREd%2BQE6Pn%2FxuHpLf9PZMDrW9fFnVypvWMNfR0xs9wzjYD6VZUqaggVvYGVsKbNCbw3npylGZ1ImZtAC8lB4fsGU0JDoIaEv6OLuXBw%2FKQ6RsakwRGOlMsPLdvVkZAewc1ra5DZZ5X5VW%2BoWYhJjP61b9Hx8rg; auth-token=75500%2FGIOSREd%2BQE6Pn%2FxuHpLf9PZMDrW9fFnVypvWMNfR0xs9wzjYD6VZUqaggVvYGVsKbNCbw3npylGZ1ImZtAC8lB4fsGU0JDoIaEv6OLuXBw%2FKQ6RsakwRGOlMsPLdvVkZAewc1ra5DZZ5X5VW%2BoWYhJjP61b9Hx8rg; uid=10764951; seller-auth-erp-url=https%3A%2F%2Ferp.lingxing.com%2Fapi%2Fseller%2FoauthRedirect; isNeedReset=0; isUpdatePwd=0; isLogin=true; zid=10764951; info=%7B%22uid%22%3A%2210764951%22%2C%22zid%22%3A%2210764951%22%2C%22username%22%3A%22m.9092G8WHM8pn%22%2C%22siteUsername%22%3A%22%22%2C%22realname%22%3A%22%E8%B6%85%E7%BA%A7%E7%AE%A1%E7%90%86%E5%91%98%22%2C%22mobile%22%3A%2217350199092%22%2C%22nationCode%22%3A%2286%22%2C%22adminNationCode%22%3A%2286%22%2C%22mealInfo%22%3A%7B%22recharge_num%22%3A0%7D%2C%22loginGuide%22%3Afalse%2C%22loginEnv%22%3A1%2C%22isPartner%22%3A0%2C%22email%22%3A%22%22%2C%22sysSubAdminFlag%22%3A0%2C%22is_mobile_verified%22%3A0%2C%22is_master%22%3A1%2C%22is_email_verified%22%3A0%2C%22hide_init_guide%22%3A0%2C%22mp_hide_init_guide%22%3A0%2C%22has_bind_oauth_center%22%3A0%2C%22has_bind_jst%22%3A0%2C%22feature_info%22%3A%7B%7D%2C%22customer_id%22%3A%2210764951%22%2C%22show_zid%22%3A%2210764951%22%2C%22available_env%22%3A%5B%22amazon%22%5D%2C%22api_info%22%3A%5B%5D%7D; sensor-distinace-id=10764951-10764951; is_sellerAuth=0; token=75500%2FGIOSREd%2BQE6Pn%2FxuHpLf9PZMDrW9fFnVypvWMNfR0xs9wzjYD6VZUqaggVvYGVsKbNCbw3npylGZ1ImZtAC8lB4fsGU0JDoIaEv6OLuXBw%2FKQ6RsakwRGOlMsPLdvVkZAewc1ra5DZZ5X5VW%2BoWYhJjP61b9Hx8rg; udesk_info_901556342054979072=%7B%22level%22%3A%22%22%2C%22klevel%22%3A%22%22%2C%22company_id%22%3A%22901556342054979072%22%2C%22customer_id%22%3A%2210764951%22%7D; Hm_lpvt_e1b07b01489084694814b73e755122ea=1744706020'
}


        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, data=payload) as response:
                if response.status == 200:
                    return await response.text()
                raise Exception(f"Request failed with status code {response.status}")
        raise

    @classmethod
    def parse_info(cls, html, url):
        logger.info(html)
        false = False
        true = True
        try:
            data = eval(re.findall(f'__INIT_DATA=(.*?)</script>', html.replace("\n", " "))[0])
            return data.get("globalData", {})
        except Exception as e:
            logger.exception(e)
            return {}

    @classmethod
    async def spider_1688_info_task(cls, url):
        try:
            # product_id = get_1688_product_id(url)
            # if product_id:
            html = await cls.get_html(url)
            data = cls.parse_info(html, url)
            return await cls.parse_data(data, url)
        except Exception as e:
            return {}

    @classmethod
    async def parse_data(cls, data, url):
        company_name = data.get("tempModel", {}).get("companyName", None)
        if not company_name:
            company_name = json.loads(data.get("offerDomain", "{}")).get("sellerModel", {}).get("companyName", None)
        seller_member_id = data.get("tempModel", {}).get("sellerMemberId", None)
        offer_id = data.get("tempModel", {}).get("offerId", None)
        if not offer_id:
            offer_id = get_1688_product_id(url)
        sku_info_map = data.get("skuModel", {}).get("skuInfoMap", {})
        if type(sku_info_map) == dict:
            sku_info_map = list(sku_info_map.values())
            for i in sku_info_map:
                i["offer_id"] = offer_id
        if company_name:
            document = await app.ctx.mongo[Supplier.collection_name].find_one(
                {"sellerMemberId": {"$eq": seller_member_id}})
            if not document:
                uuid = get_uuid()
                await app.ctx.mongo[Supplier.collection_name].insert_one({
                    "uuid": uuid,
                    "name": company_name,
                    "sellerMemberId": seller_member_id,
                })
                return {"uuid": uuid, "sku_info_map": sku_info_map if sku_info_map else [
                    {"specId": "", "specAttrs": "默认款式(无变体)", "offer_id": offer_id}]}
            else:
                return {"uuid": document.get("uuid", None), "sku_info_map": sku_info_map if sku_info_map else [
                    {"specId": "", "specAttrs": "默认款式(无变体)", "offer_id": offer_id}]}


class SkuMap1688():
    TOKEN = None
    @classmethod
    @retry(stop_max_attempt_number=3, wait_random_min=100, wait_random_max=1000)
    async def get_sku_data(cls, product_id):
        url = f"""https://erp.lingxing.com/api/module/purchase1688/Purchase1688Product/batchGetInfoByProductLink?link[]=https:%2F%2Fdetail.1688.com%2Foffer%2F{product_id}.html&req_time_sequence=%2Fapi%2Fmodule%2Fpurchase1688%2FPurchase1688Product%2FbatchGetInfoByProductLink$$5"""
        payload = {}
        headers = {
  'AK-Client-Type': 'web',
  'AK-Origin': 'https://erp.lingxing.com',
  'Accept': 'application/json, text/plain, */*',
  'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
  'Cache-Control': 'no-cache',
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Referer': 'https://erp.lingxing.com/erp/pairingManage',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
  'auth-token': '3c43YZd4/shX+g6jFJH9dQiXYQo5Us6jYHkrM2fWuL7UlianYzId9e2u1ARdxwiWOx6/Fl/1ZfYSYxrvfX4lK3pVqcq5SOrpO/BupcV7Yb7ysO7TnlUXH1L9dkdFAZUn1NkfdYSS3ufsdKIBfnZQpP2IsBxb82eqk9Qq3N8'
}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, data=payload) as response:
                if response.status == 200:
                    return await response.json()
                raise Exception(f"Request failed with status code {response.status}")
        raise

    @classmethod
    async def spider_1688_info_task(cls, url, campany_id):
        try:
            # product_id = get_1688_product_id(url)
            # if product_id:
            data = await cls.get_sku_data(product_id=get_1688_product_id(url))
            return await cls.parse_data(data, url, campany_id)
        except Exception as e:
            logger.exception(e)
            return {}

    @classmethod
    async def parse_data(cls, data, url, campany_id):
        if data.get("code", None) != 1 or not data.get("data", []):
            raise Exception(str(data))
        data = data.get("data", [])[0]
        company_name = data.get("cross_basic_info", {}).get("companyName", None)
        seller_member_id = data.get("cross_basic_info", {}).get("loginId", None)
        shop_url = data.get("cross_basic_info", {}).get("shopUrl", None)
        offer_id = data.get("product_id", None)
        try:
            images = data.get("image", {}).get("images", [])
        except:
            images = []
        if not offer_id:
            offer_id = get_1688_product_id(url)
        sku_infos = data.get("sku_infos", [])
        sku_info_map = []
        for i in sku_infos:
            sku_info_map.append({
                "offer_id": offer_id,
                "skuId": i.get("sku_id", None),
                "specAttrs": " && ".join([j.get("attribute_value", "空属性") for j in i.get("attributes", [])]),
                "specId": i.get("spec_id", None)
            })
        if company_name:
            document = await app.ctx.mongo[Supplier.collection_name].find_one(
                {"sellerMemberId": {"$eq": seller_member_id}, "campanyId": {"$eq": campany_id}})
            if not document:
                uuid = get_uuid()
                await app.ctx.mongo[Supplier.collection_name].insert_one({
                    "campanyId": campany_id,
                    "uuid": uuid,
                    "name": company_name,
                    "url": shop_url,
                    "sellerMemberId": seller_member_id,
                })
                return {"uuid": uuid, "sku_info_map": sku_info_map if sku_info_map else [
                    {"specId": "", "specAttrs": "默认款式(无变体)", "offer_id": offer_id}],"images":images}
            else:
                return {"uuid": document.get("uuid", None), "sku_info_map": sku_info_map if sku_info_map else [
                    {"specId": "", "specAttrs": "默认款式(无变体)", "offer_id": offer_id}],"images":images}
