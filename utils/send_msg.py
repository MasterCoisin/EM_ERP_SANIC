# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BACKEN 
@File        ：send_msg.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024-09-07 0:28 
-------------------------------------
'''
import json
import time

import requests
from retrying import retry


@retry(stop_max_attempt_number=5, wait_random_min=1000, wait_random_max=2000)
def send_to_fei_shu(msg):
    data = json.dumps({
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": "通知:",
                    "content": msg
                }
            }
        }
    })
    resp = requests.post(url="https://open.feishu.cn/open-apis/bot/v2/hook/48a2fe4a-8337-4688-b9b8-56496cbe1e29",
                         data=data)
    time.sleep(1)