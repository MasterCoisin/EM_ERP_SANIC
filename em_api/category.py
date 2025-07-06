# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BACKEN 
@File        ：category.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：类目数据api
@Date        ：2024-04-30 10:56 
-------------------------------------
'''
import json

import requests
from em_api.constant import HASH
from retrying import retry


class CategoryApi():
    @classmethod
    @retry(stop_max_attempt_number=3, wait_random_min=100, wait_random_max=1000)
    def read(cls, current_page, items_per_page=100, category_id=None,language="en"):
        url = f"https://marketplace.emag.ro/api-3/category/read?language={language}"
        if category_id:
            data = json.dumps({
                'currentPage': current_page,
                'itemsPerPage': items_per_page,
                "id": category_id
            })
        else:
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

    @classmethod
    @retry(stop_max_attempt_number=3, wait_random_min=100, wait_random_max=1000)
    def count(cls):
        headers = {
            'Authorization': 'Basic ' + HASH
        }
        response = requests.post('https://marketplace.emag.ro/api-3/category/count', headers=headers)
        return response.json()
