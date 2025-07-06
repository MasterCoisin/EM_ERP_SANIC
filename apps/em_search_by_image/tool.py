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
@Date        ：2025-04-29 19:13 
-------------------------------------
'''
import asyncio
import aiohttp
import json

import httpx


async def get_em_search_result(image):
    url = "https://sapi.emag.ro/search-by-filters-with-redirect?fields%5Bitems%5D%5Bimage_gallery%5D%5Bfashion%5D%5Blimit%5D=8&fields%5Bquick_filters%5D=1&from_filters=false&no_supermarket=1&page%5Blimit%5D=24&page%5Boffset%5D=0&templates%5B%5D=custom_lite"
    payload = json.dumps({
        "image": image
    })
    headers = {
        'Host': 'sapi.emag.ro',
        'Accept': '*/*',
        'X-App-Screen-Id': '4A509447-BA8E-431D-98A7-1273F4F4BDA8',
        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'X-AB-Tests-Auto': '{"tgt_eab_1463":"A","easybox_shipping_tax_value":"a","tgt_eab_1466":"C","tgt_eab_1473":"B","tgt_ads_zscore":"A"}',
        'Content-Type': 'application/json',
        'Content-Length': str(len(payload)),
        'X-Request-Source': 'mobile-app',
        'User-Agent': 'eMAG/3.38.2 (iPhone14,8; iOS 16.0.2; Alamofire; 1284x2778)',
        'Referer': 'https://www.emag.ro/search/searchresults',
        'X-App-Version': 'iOS-3.38.2',
        'Connection': 'keep-alive'
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, data=payload)
            response.raise_for_status()
            json_response = response.json()
            return json_response
        except httpx.HTTPStatusError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except json.JSONDecodeError as json_err:
            print(f"JSON decoding error occurred: {json_err}")
        except Exception as err:
            print(f"An unexpected error occurred: {err}")
