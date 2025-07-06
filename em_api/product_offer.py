# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BACKEN 
@File        ：product_offer_read.py
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

import aiohttp
import requests
from tenacity import retry, stop_after_attempt, wait_random
from loguru import logger


class ProductOfferApi:
    @classmethod
    @retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2))
    def readNormal(cls, shop_hash, current_page, items_per_page=100, language="en", country="ro"):
        try:
            url = f"https://marketplace.emag.{country}/api-3/product_offer/read?language={language}"
            headers = {
                'Authorization': f'Basic {shop_hash}',
                'Content-Type': 'application/json'
            }
            data = json.dumps({
                "currentPage": current_page,
                "itemsPerPage": items_per_page
            })
            response = requests.request("POST", "http://47.122.135.75:11234/api/post/", headers=headers,
                                        json={"url": url, "headers": headers, "data": data}, timeout=20)
            return response.json()
        except Exception as e:
            logger.exception(e)
            raise e

    @classmethod
    @retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2))
    async def read(cls, shop_hash, current_page, items_per_page=100, language="en", country="ro"):
        url = f"https://marketplace.emag.{country}/api-3/product_offer/read?language={language}"
        headers = {
            'Authorization': f'Basic {shop_hash}',
            'Content-Type': 'application/json'
        }
        payload = {
            "currentPage": current_page,
            "itemsPerPage": items_per_page
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=20) as response:
                response_data = await response.json()
                if response_data.get("isError"):
                    print(f"API Error: {response_data}")
                    raise aiohttp.ClientError("API returned error response")
                return response_data

    @classmethod
    @retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2))
    def countNormal(cls, shop_hash, country="ro"):
        try:
            url = f"https://marketplace.emag.{country}/api-3/product_offer/count"
            headers = {'Authorization': f'Basic {shop_hash}'}

            response = requests.request("POST", "http://47.122.135.75:11234/api/post/", headers=headers,
                                        json={"url": url, "headers": headers, "data": {}}, timeout=20)
            return response.json()
        except Exception as e:
            logger.exception(e)
            raise e

    @classmethod
    @retry(stop=stop_after_attempt(3), wait=wait_random(min=1, max=2))
    async def count(cls, shop_hash, country="ro"):
        url = f"https://marketplace.emag.{country}/api-3/product_offer/count"
        headers = {'Authorization': f'Basic {shop_hash}'}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers) as response:
                response_data = await response.json()
                if response_data.get("isError"):
                    raise aiohttp.ClientError("Count API error")
                return response_data

    @classmethod
    @retry(stop=stop_after_attempt(3), wait=wait_random(min=0.1, max=1))
    async def save(cls, shop_hash, data, country="ro"):
        url = f"https://marketplace.emag.{country}/api-3/product_offer/save"
        headers = {
            'Authorization': f'Basic {shop_hash}',
            'Content-Type': 'application/json'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                return await response.json()
