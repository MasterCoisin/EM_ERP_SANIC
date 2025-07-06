# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BACKEN 
@File        ：order_read.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024-05-22 10:58 
-------------------------------------
'''
import json
from loguru import logger
import requests
from retrying import retry
from utils.models import ModelManager
from utils.json_tools import save_json


class OrderApi():
    @classmethod
    @retry(stop_max_attempt_number=3, wait_random_min=100, wait_random_max=1000)
    def read(cls, shop_hash, current_page, items_per_page=100, country="ro", language="en", modifiedAfter=None,
             modifiedBefore=None):
        try:
            url = f"https://marketplace.emag.{country}/api-3/order/read"  # ?language={language}
            if modifiedAfter:
                data = json.dumps({
                    'currentPage': current_page,
                    'itemsPerPage': items_per_page,
                    'modifiedAfter': modifiedAfter,
                    'modifiedBefore': modifiedBefore
                })
            else:
                data = json.dumps({
                    'currentPage': current_page,
                    'itemsPerPage': items_per_page
                })
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Basic {shop_hash}'
            }
            # response = requests.request("POST", url, headers=headers, data=data, proxies=proxies, timeout=20)
            response = requests.request("POST", "http://47.122.135.75:11234/api/post/", headers=headers,
                                        json={"url": url, "headers": headers, "data": data}, timeout=20)
            return response.json()
        except Exception as e:
            logger.exception(e)
            raise e

    @classmethod
    @retry(stop_max_attempt_number=3, wait_random_min=100, wait_random_max=1000)
    def count(cls, shop_hash, country="ro"):
        try:
            url = f'https://marketplace.emag.{country}/api-3/order/count'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Basic {shop_hash}'
            }
            # response = requests.request("POST", url, headers=headers, data=data, proxies=proxies, timeout=20)
            response = requests.request("POST", "http://47.122.135.75:11234/api/get/", headers=headers,
                                        json={"url": url, "headers": headers}, timeout=20)
            return response.json()
        except Exception as e:
            logger.exception(e)
            raise e

    @classmethod
    @retry(stop_max_attempt_number=3, wait_random_min=100, wait_random_max=1000)
    def save(cls, shop_hash, data):
        url = f"https://marketplace.emag.ro/api-3/order/save"  # ?language={language}
        data = json.dumps(data)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {shop_hash}'
        }
        response = requests.request("POST", url, headers=headers, data=data)
        return response.json()

# print(OrderApi.read(1, 5, createdAfter="2024-08-27 17:27:24"))
