# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：em_ads_credits_data_async.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：广告充值数据同步
@Date        ：2025-06-19 10:22 
-------------------------------------
'''
import datetime
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from loguru import logger
from retrying import retry
from tqdm import tqdm

from utils.common import to_mongo
from utils.models import ModelManager


class adsCreditsSpider(object):
    PER = 100

    def __init__(self, shop_id, campany_id, shop_info):
        self.campany_id = campany_id
        self.shop_id = shop_id
        self.shop_info = shop_info
        self.cookie_ro = self.shop_info.get("em_login_info", {}).get("cookie_ro", None)
        self.cookie_bg = self.shop_info.get("em_login_info", {}).get("cookie_bg", None)
        self.cookie_hu = self.shop_info.get("em_login_info", {}).get("cookie_hu", None)
        self.cookie = {
            "ro": self.cookie_ro,
            "bg": self.cookie_bg,
            "hu": self.cookie_hu
        }

    @retry(stop_max_attempt_number=3, wait_random_min=100, wait_random_max=1000)
    def get_ads_credits_records_count(self, country):
        url = f"https://marketplace.emag.{country}/api-ui/ads-credits/count"
        payload = {}
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Referer': 'https://marketplace.emag.ro/ads/credits?credit_type=0&credit_type=1&credit_type=2',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Cookie': self.cookie[country]
        }

        response = requests.request("GET", url, headers=headers, data=payload, proxies=PROXIES, timeout=10)
        if response.status_code == 200:
            return True, response.json().get("count", 0)
        else:
            return False, None

    @retry(stop_max_attempt_number=3, wait_random_min=100, wait_random_max=1000)
    def get_ads_credits_records_list(self, country, page):
        url = f"https://marketplace.emag.{country}/api-ui/ads-credits/list?page={page}&items_per_page={self.PER}"
        payload = {}
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Referer': 'https://marketplace.emag.ro/ads/credits?credit_type=0&credit_type=1&credit_type=2',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Cookie': self.cookie[country]
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, []

    def run(self, country):
        logger.info(f"shop->{self.shop_id} country->{country}")
        try:
            is_ok, count = self.get_ads_credits_records_count(country)
            if not is_ok:
                return
            logger.info(f"总充值记录数->{count}")
            for page in tqdm(range(1, count // self.PER + 2)):
                try:
                    is_ok, result = self.get_ads_credits_records_list(country=country, page=page)
                    if not is_ok:
                        return
                    if result:
                        adds = []
                        for item in result:
                            adds.append({
                                "campanyId": self.campany_id,
                                "shop": self.shop_id,
                                "country": country,
                                "creditId": item.get("credit_id", None),
                                "creditStatus": item.get("credit_status", None).split(".",)[-1] if item.get(
                                    "credit_status", None) else item.get("credit_status", None),
                                "creditType": item.get("credit_type", None).split(".")[-1] if item.get(
                                    "credit_type", None) else item.get("credit_type", None),
                                "sellerName": item.get("seller_name", None),
                                "sellerLink": item.get("seller_link", None),
                                "creditLink": item.get("credit_link", None),
                                "activationDate": datetime.datetime.strptime(item.get("activation_date", None),
                                                                             "%d-%m-%Y") if item.get(
                                    "activation_date", None) else item.get("activation_date", None),
                                "expirationDate": datetime.datetime.strptime(item.get("expiration_date", None),
                                                                             "%d-%m-%Y") if item.get(
                                    "expiration_date", None) else item.get("expiration_date", None),
                                "creditValue": item.get("credit_value", None),
                                "creditClicks": float(item.get("credit_clicks", None)) if item.get("credit_clicks",
                                                                                                   None) else item.get(
                                    "credit_clicks", None),
                                "availableCredit": float(item.get("available_credit", None)) if item.get(
                                    "available_credit",
                                    None) else item.get(
                                    "available_credit", None)
                            })
                        to_mongo(ads_credit_records_model, adds, ['campanyId', 'shop', 'country', 'creditId'])
                except Exception as e:
                    logger.exception(e)
        except Exception as e:
            logger.exception(e)


def loop():
    shop_objs = shop_model.objects(em_login_info__hash__ne=None).only("shop_id", "campanyId", "em_login_info")
    pool = ThreadPoolExecutor(5)
    for shop_obj in shop_objs:
        campany_id = shop_obj.campanyId
        if not campany_model.objects(campanyId=campany_id, isSvip=True).first():
            continue
        for country in ["ro", "bg", "hu"]:
            pool.submit(
                adsCreditsSpider(shop_obj.shop_id, shop_obj.campanyId, {"em_login_info": shop_obj.em_login_info}).run,
                country)
    pool.shutdown(wait=True)


def main():
    while True:
        loop()
        time.sleep(60 * 60 * 24)


if __name__ == '__main__':
    PROXIES = {"https": 'http://127.0.0.1:10809', "http": 'http://127.0.0.1:10809'}
    campany_model = ModelManager.get_model("campany", "base")
    shop_model = ModelManager.get_model("shop", "base")
    ads_credit_records_model = ModelManager.get_model("ads_credit_records", "base")
    main()
