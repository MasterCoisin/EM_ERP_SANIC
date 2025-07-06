# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：em_shop_manager.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-03-29 17:10 
-------------------------------------
'''
import httpx
import requests
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorCollection
from lxml import etree
from sanic import Sanic
from apps.shop.tool import get_shop_1688_token, get_shop_info, update_shop_cookie

from config.constant import APP_NAME
from cores.otpManager import otp_create
from models.shop import Shop
from mongodb_tool.db_list import mongodb_list


class EmShopManager(object):
    APP = Sanic.get_app(APP_NAME)
    SHOP_DICT = {}

    def __init__(self, shop_id):
        EmShopManager.SHOP_DICT[shop_id] = self
        self.shop_id = shop_id
        self.shop_info = {}
        self.username = None
        self.password = None
        self.hash = None
        self.cookie = None

    async def init(self):
        shop_info = await get_shop_info(shop_id=self.shop_id)
        self.shop_info = shop_info
        self.username = shop_info.get("em_login_info", {}).get("username", None)
        self.password = shop_info.get("em_login_info", {}).get("password", None)
        self.hash = shop_info.get("em_login_info", {}).get("hash", None)
        self.otp = shop_info.get("em_login_info", {}).get("otp", None)
        self.cookie = shop_info.get("em_login_info", {}).get("cookie", None)
        if not self.cookie and self.username and self.password:
            await self._login_em()

    async def _login_em(self):
        logger.info("login")
        url = "https://auth.emag.net/login_check?adk=rG1UHvzLwaWTi0WG"
        payload = f"_username={self.username.replace('@', '%40')}&_password={self.password}"
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,ro;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://auth.emag.net',
            'Pragma': 'no-cache',
            'Referer': 'https://auth.emag.net/login?_locale=cn&adk=rG1UHvzLwaWTi0WG',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        try:
            response = requests.request("POST", url, headers=headers, data=payload, allow_redirects=False)
            cookie = response.cookies.items()
            if response.status_code == 302:
                response = requests.request("GET", response.headers["Location"], cookies=response.cookies,
                                            allow_redirects=False)
                if response.status_code == 200:
                    self.cookie = ";".join([f"{i[0]}={i[1]}" for i in cookie])
                    await self._save_cookie()
                elif response.status_code == 302:
                    response = requests.request("POST", url, headers=headers, data=payload)
                    html = etree.HTML(response.text)
                    otp_token = html.xpath(r'//*[@id="otp__token"]/@value')
                    if response.status_code==200 and otp_token:
                        if self.otp:
                            otp = otp_create(self.otp)
                            payload = f'otp%5Botp%5D={otp}&otp%5B_token%5D={otp_token[0]}'
                            response = requests.request("POST", "https://auth.emag.net/2fa/validate-otp", headers=headers, data=payload)
                            if response.status_code==200:
                                self.cookie = ";".join([f"{i[0]}={i[1]}" for i in cookie])
                                await self._save_cookie()



        except EmShopManager as e:
            logger.exception(e)

    async def _save_cookie(self):
        await update_shop_cookie(shop_id=self.shop_id, cookie=self.cookie)

    @classmethod
    async def loop(cls):
        shops = await mongodb_list(collection_name=Shop.collection_name, fields=[], filters=[], sorts=[],
                           current_page=1, page_size=100)
        for shop in shops["data"]:
            await EmShopManager(shop_id=shop.get("shop_id")).init()
