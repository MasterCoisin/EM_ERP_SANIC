# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BACKEN 
@File        ：vat.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024-05-23 22:37 
-------------------------------------
'''
import json

import requests
from em_api.constant import HASH
from retrying import retry


class VatApi():
    @classmethod
    @retry(stop_max_attempt_number=3, wait_random_min=100, wait_random_max=1000)
    def read(cls, current_page, items_per_page=100, language="en"):
        url = f"https://marketplace.emag.ro/api-3/vat/read"  # ?language={language}
        data = json.dumps({
            'currentPage': current_page,
            'itemsPerPage': items_per_page
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {HASH}'
        }
        response = requests.request("POST", url, headers=headers, data=data)
        return response.json()

print(VatApi.read(1))