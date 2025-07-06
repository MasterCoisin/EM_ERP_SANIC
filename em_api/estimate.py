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

import aiohttp
import requests
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_random


class EstimateApi:
    @classmethod
    @retry(stop=stop_after_attempt(3), wait=wait_random(min=0.1, max=1))  # 保持原始重试间隔（100-1000毫秒）
    async def read(cls, extId,shop_hash, country="ro"):
        url = f"https://marketplace.emag.{country}/api/v1/commission/estimate/{extId}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {shop_hash}'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                # 检查 HTTP 状态码
                if response.status != 200:
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=f"HTTP Error: {response.status}"
                    )

                # 尝试解析 JSON
                try:
                    data = await response.json()
                except aiohttp.ContentTypeError as e:
                    raise ValueError("Invalid JSON response") from e

                return data

    @classmethod
    def readSync(cls, extId,shop_hash, country="ro"):
        try:
            url = f"https://marketplace.emag.{country}/api/v1/commission/estimate/{extId}"
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
