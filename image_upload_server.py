# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：image_upload_server.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-05-12 14:09 
-------------------------------------
'''
import time

import requests

from utils.models import ModelManager
from concurrent.futures import ThreadPoolExecutor


def save_img_(cookie, file_name,sourceImgFile, try_times=1):
    try:
        url = "https://marketplace.emag.ro/resource/upload"
        payload = {}
        files = [
            ('file[file]', (file_name, sourceImgFile, 'image/jpeg'))
        ]

        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': cookie,
            'Origin': 'https://marketplace.emag.ro',
            'Referer': 'https://marketplace.emag.ro/product/new',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }

        response = requests.request("POST", url, headers=headers, data=payload, files=files, timeout=10)
        print(response.json())

        url = response.json()["url"]

        if url:
            return True, url
        else:
            try_times -= 1
            if try_times:
                return save_img_(cookie, file_name,sourceImgFile, try_times)
            else:
                return False, "上传失败"
    except Exception as e:
        try_times -= 1
        if try_times:
            return save_img_(cookie, file_name,sourceImgFile, try_times)
        else:
            return False,"上传失败"


def upload(obj, cookies):
    for cookie in cookies:
        is_ok, emUrl = save_img_(cookie, f"{obj.sourceId}.jpg", obj.sourceImgFile)
        if is_ok:
            obj.update(emUrl=emUrl)
            return


def task():
    shop_objs = shop_model.objects(em_login_info__cookie__ne=None).only("em_login_info__cookie")
    cookies = [i.em_login_info.get("cookie", None) for i in shop_objs]
    objs = images_model.objects(emUrl=None).only("emUrl", "sourceId", "sourceImgFile")
    pool = ThreadPoolExecutor(10)
    for obj in objs:
        pool.submit(upload,obj, cookies)
    pool.shutdown(wait=True)



def main():
    while True:
        task()
        time.sleep(60)


if __name__ == '__main__':
    shop_model = ModelManager.get_model("shop", "base")
    images_model = ModelManager.get_model("images", "base")
    main()
