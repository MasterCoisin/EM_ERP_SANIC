# # -*- coding: UTF-8 -*-
# '''
# @Project     ：EM_ERP_BACKEN
# @File        ：access_token_manager.py
# @IDE         ：PyCharm
# -------------------------------------
# @Author      ：Coisin
# @QQ          ：2849068933
# @PHONE       ：17350199092
# @Description ：
# @Date        ：2024-07-02 12:05
# -------------------------------------
# '''
# import asyncio
# from loguru import logger
# import time
# import httpx
# from utils.json_tools import *
# from config.constant import FEISHU_CONFIG
#
#
# class AccessTokenManager():
#     app_access_token = None
#     tenant_access_token = None
#
#     def __init__(self):
#         self.access_expire_time = None
#
#     async def get_access_token(self):
#         url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
#         req_body = {"app_id": FEISHU_CONFIG["app_id"], "app_secret": FEISHU_CONFIG["app_secret"]}
#         async with httpx.AsyncClient() as client:
#             resp = await client.post(url, data=req_body)
#             response = resp.json()
#             if response["code"] == 0:
#                 AccessTokenManager.app_access_token = response["app_access_token"]
#                 print(AccessTokenManager.app_access_token, response["expire"], time.time())
#                 self.access_expire_time = time.time() + response["expire"] - 240
#
#     async def get_tenant_access_token(self):
#         url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
#         req_body = {"app_id": FEISHU_CONFIG["app_id"], "app_secret": FEISHU_CONFIG["app_secret"]}
#         async with httpx.AsyncClient() as client:
#             resp = await client.post(url, data=req_body)
#             response = resp.json()
#             if response["code"] == 0:
#                 AccessTokenManager.tenant_access_token = response["tenant_access_token"]
#                 print(AccessTokenManager.tenant_access_token)
#
#     async def update_token(self):
#         await self.get_access_token()
#         # self.get_tenant_access_token()
#         data = read_json("/home/em/baken/config/fs_token.json")
#         data["app_access_token"] = AccessTokenManager.app_access_token
#         data["tenant_access_token"] = AccessTokenManager.app_access_token
#         save_json(data, "/home/em/baken/config/fs_token.json")
#
#     async def refresh_token(self):
#         print(1111111111111111111111)
#         await self.update_token()
#         while True:
#             await asyncio.sleep(60)
#             try:
#                 if self.access_expire_time and time.time() >= self.access_expire_time:
#                     await self.update_token()
#             except Exception as e:
#                 logger.exception(e)
#
#
#
# async def get_user_access_token(code):
#     url = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"
#     req_body = {
#         "grant_type": "authorization_code",
#         "code": code
#     }
#     headers = {
#         "Authorization": f"Bearer {AccessTokenManager.app_access_token}",
#         "Content-Type": "application/json; charset=utf-8"
#     }
#     async with httpx.AsyncClient() as client:
#         resp = await client.post(url, data=req_body, headers=headers)
#         response = resp.json()
#         if response["code"] == 0:
#             return response["data"]["access_token"]
#         return False
#
#
# async def get_user_info(code):
#     user_access_token = await get_user_access_token(code=code)
#     if user_access_token:
#         url = "https://open.feishu.cn/open-apis/authen/v1/user_info"
#         headers = {
#             "Authorization": f"Bearer {user_access_token}",
#             "Content-Type": "application/json; charset=utf-8"
#         }
#         async with httpx.AsyncClient() as client:
#             resp = await client.post(url, headers=headers)
#             response = resp.json()
#             if response["code"] == 0:
#                 return response["data"]
#             return {}
#     return {}
# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BACKEN
@File        ：access_token_manager.py
@IDE         ：PyCharm
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024-07-02 12:05
-------------------------------------
'''
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import httpx
from sanic import Sanic

from utils.json_tools import *
import requests

from config.constant import FEISHU_CONFIG, APP_NAME


class AccessTokenManager():
    # app_access_token = None
    # tenant_access_token = None
    app = Sanic.get_app(APP_NAME)

    def __init__(self):
        self.access_expire_time = None
        self.pool = ThreadPoolExecutor(1)
        self.update_token()
        self.pool.submit(self.refresh_token)

    def get_access_token(self):
        url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
        req_body = {"app_id": FEISHU_CONFIG["app_id"], "app_secret": FEISHU_CONFIG["app_secret"]}
        response = requests.post(url, req_body).json()
        if response["code"] == 0:
            AccessTokenManager.app.shared_ctx.cache["app_access_token"] = response["app_access_token"]
            print(AccessTokenManager.app.shared_ctx.cache["app_access_token"], response["expire"], time.time())
            self.access_expire_time = time.time() + response["expire"] - 240

    # def get_tenant_access_token(self):
    #     url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    #     req_body = {"app_id": FEISHU_CONFIG["app_id"], "app_secret": FEISHU_CONFIG["app_secret"]}
    #     response = requests.post(url, req_body).json()
    #     if response["code"] == 0:
    #         AccessTokenManager.tenant_access_token = response["tenant_access_token"]
    #         print(AccessTokenManager.tenant_access_token)

    def update_token(self):
        self.get_access_token()
        # self.get_tenant_access_token()
        data = read_json("config/fs_token.json")
        data["app_access_token"] = AccessTokenManager.app.shared_ctx.cache.get("app_access_token", None)
        data["tenant_access_token"] = AccessTokenManager.app.shared_ctx.cache.get("app_access_token", None)
        save_json(data, "config/fs_token.json")

    def refresh_token(self):
        while True:
            time.sleep(60)
            if self.access_expire_time and time.time() >= self.access_expire_time:
                self.update_token()


async def get_user_access_token(code):
    url = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"
    req_body = json.dumps({
        "grant_type": "authorization_code",
        "code": code
    })
    print(AccessTokenManager.app.shared_ctx.cache.get("app_access_token", None))
    headers = {
        "Authorization": f"Bearer {AccessTokenManager.app.shared_ctx.cache.get('app_access_token', None)}",
        "Content-Type": "application/json; charset=utf-8"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, data=req_body, headers=headers)
        response = resp.json()
        print(response)
        if response["code"] == 0:
            return response["data"]["access_token"]
        return False


async def get_user_info(code):
    user_access_token = await get_user_access_token(code=code)
    if user_access_token:
        url = "https://open.feishu.cn/open-apis/authen/v1/user_info"
        headers = {
            "Authorization": f"Bearer {user_access_token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            response = resp.json()
            if response["code"] == 0:
                return response["data"]
            return {}
    return {}

