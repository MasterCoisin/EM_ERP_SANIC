# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：em_shop_cookie_manager.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-05-12 9:52 
-------------------------------------
'''
import time

import requests
from DrissionPage._configs.chromium_options import ChromiumOptions
from loguru import logger
from lxml import etree

from cores.otpManager import otp_create
from utils.models import ModelManager
from DrissionPage import Chromium

from concurrent.futures import ThreadPoolExecutor


class EmShopManager(object):

    def __init__(self, shop_id, campany_id, shop_info):
        self.campany_id = campany_id
        self.shop_id = shop_id
        self.shop_info = shop_info
        self.username = None
        self.password = None
        self.hash = None
        self.need_otp = False
        self.cookie_ro = None
        self.cookie_bg = None
        self.cookie_hu = None

    def init(self):
        self.username = self.shop_info.get("em_login_info", {}).get("username", None)
        self.password = self.shop_info.get("em_login_info", {}).get("password", None)
        self.hash = self.shop_info.get("em_login_info", {}).get("hash", None)
        self.otp = self.shop_info.get("em_login_info", {}).get("otp", None)
        self.need_otp = self.shop_info.get("em_login_info", {}).get("need_otp", False)
        self.cookie_ro = self.shop_info.get("em_login_info", {}).get("cookie_ro", None)
        self.cookie_bg = self.shop_info.get("em_login_info", {}).get("cookie_bg", None)
        self.cookie_hu = self.shop_info.get("em_login_info", {}).get("cookie_hu", None)

        if self.username and self.password:
            if not self.cookie_ro:
                self._login_em()
            else:
                self.check_login_ro()
            if not self.cookie_bg:
                self._login_em()
            else:
                self.check_login_bg()
            if not self.cookie_hu:
                self._login_em()
            else:
                self.check_login_hu()

    def check_login_ro(self):
        url = "https://marketplace.emag.ro/legal/list"
        payload = {}
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Referer': 'https://marketplace.emag.ro/legal/list/192750',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
            'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Cookie': self.cookie_ro
        }
        response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)
        logger.info(response.headers.get("Location", ""))
        if "/legal/list/" not in response.headers.get("Location", ""):
            self._login_em()
        else:
            self._save_user_id_ro(response.headers.get("Location", "").split("/")[-1])

    def check_login_bg(self):
        url = "https://marketplace.emag.bg/legal/list"
        payload = {}
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Referer': 'https://marketplace.emag.ro/legal/list/192750',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
            'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Cookie': self.cookie_bg
        }
        response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)
        logger.info(response.headers.get("Location", ""))
        if "/legal/list/" not in response.headers.get("Location", ""):
            self._login_em()
        else:
            self._save_user_id_bg(response.headers.get("Location", "").split("/")[-1])

    def check_login_hu(self):
        url = "https://marketplace.emag.hu/legal/list"
        payload = {}
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Referer': 'https://marketplace.emag.ro/legal/list/192750',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
            'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Cookie': self.cookie_hu
        }
        response = requests.request("GET", url, headers=headers, data=payload, allow_redirects=False)
        logger.info(response.headers.get("Location", ""))
        if "/legal/list/" not in response.headers.get("Location", ""):
            self._login_em()
        else:
            self._save_user_id_hu(response.headers.get("Location", "").split("/")[-1])
    def _login_em(self):
        logger.info("login")
        if self.need_otp and not self.otp:
            return
        # 启动或接管浏览器，并获取标签页对象
        co = ChromiumOptions().auto_port()
        co.incognito()  # 匿名模式
        co.headless()  # 无头模式
        co.set_argument('--proxy-server', 'http://127.0.0.1:10809')
        broswer = Chromium(addr_or_opts=co)
        try:
            tab = broswer.latest_tab
            # 跳转到登录页面
            tab.get('https://marketplace.emag.ro/dashboard')
            # 定位到账号文本框，获取文本框元素
            ele = tab.ele('#_username')
            # 输入对文本框输入账号
            ele.input(self.username)
            #
            tab.ele('#sendBtn').click()
            tab.wait.ele_displayed('#_password')
            # 定位到密码文本框并输入密码
            tab.ele('#_password').input(self.password)
            # 点击登录按钮
            tab.ele('@type=submit').click()
            tab.wait.url_change(text="https://auth.emag.net/2fa/validate-otp", timeout=20)
            # otp
            if "2fa" in tab.url:
                tab.wait.ele_displayed('#otp_otp')
                # 更新标签，需要otp
                self._save_need_otp_status(True)
                otp = otp_create(self.otp)
                # 定位到账号文本框，获取文本框元素
                ele = tab.ele('#otp_otp')
                # 输入对文本框输入账号
                ele.input(otp)
                # 点击登录按钮
                tab.ele('@type=submit').click()
            else:
                self._save_need_otp_status(False)
            tab.wait.url_change(text="https://marketplace.emag.ro/dashboard", timeout=20)
            self.cookie_ro = ";".join([f"{i['name']}={i['value']}" for i in tab.cookies()])
            self._save_cookie()
            #
            tab.get('https://marketplace.emag.bg/dashboard')
            tab.wait.url_change(text="https://marketplace.emag.bg/dashboard", timeout=20)
            self.cookie_bg = ";".join([f"{i['name']}={i['value']}" for i in tab.cookies()])
            self._save_cookie()
            #
            tab.get('https://marketplace.emag.hu/dashboard')
            tab.wait.url_change(text="https://marketplace.emag.hu/dashboard", timeout=20)
            self.cookie_hu = ";".join([f"{i['name']}={i['value']}" for i in tab.cookies()])
            self._save_cookie()
        except Exception as e:
            pass
        finally:
            broswer.quit()

    def _save_need_otp_status(self, status):
        shop_obj = shop_model.objects(shop_id=self.shop_id, campanyId=self.campany_id).first()
        em_login_info = shop_obj.em_login_info
        em_login_info["need_otp"] = status
        shop_obj.update(em_login_info=em_login_info)

    def _save_cookie(self):
        shop_obj = shop_model.objects(shop_id=self.shop_id, campanyId=self.campany_id).first()
        em_login_info = shop_obj.em_login_info
        em_login_info["cookie_ro"] = self.cookie_ro
        em_login_info["cookie_bg"] = self.cookie_bg
        em_login_info["cookie_hu"] = self.cookie_hu
        em_login_info["lastUpdateTime"] = time.time()
        shop_obj.update(em_login_info=em_login_info)

    def _save_user_id_ro(self, userId):
        shop_obj = shop_model.objects(shop_id=self.shop_id, campanyId=self.campany_id).first()
        em_login_info = shop_obj.em_login_info
        em_login_info["userIdRo"] = userId
        shop_obj.update(em_login_info=em_login_info)

    def _save_user_id_bg(self, userId):
        shop_obj = shop_model.objects(shop_id=self.shop_id, campanyId=self.campany_id).first()
        em_login_info = shop_obj.em_login_info
        em_login_info["userIdBg"] = userId
        shop_obj.update(em_login_info=em_login_info)

    def _save_user_id_hu(self, userId):
        shop_obj = shop_model.objects(shop_id=self.shop_id, campanyId=self.campany_id).first()
        em_login_info = shop_obj.em_login_info
        em_login_info["userIdHu"] = userId
        shop_obj.update(em_login_info=em_login_info)


def loop():
    shop_objs = shop_model.objects(em_login_info__hash__ne=None).only("shop_id", "campanyId", "em_login_info")
    pool = ThreadPoolExecutor(5)
    for shop_obj in shop_objs:
        # EmShopManager(shop_obj.shop_id, shop_obj.campanyId, {"em_login_info": shop_obj.em_login_info}).init()
        pool.submit(EmShopManager(shop_obj.shop_id, shop_obj.campanyId, {"em_login_info": shop_obj.em_login_info}).init)
    pool.shutdown(wait=True)


def main():
    while True:
        loop()
        time.sleep(60 * 10)


if __name__ == '__main__':
    shop_model = ModelManager.get_model("shop", "base")
    main()
# 1747021675.98428 otpauth://totp/eMAG%3A1165621218%40qq.com?image=https%3A%2F%2Fs13emagst.akamaized.net%2Flayout%2Fro%2Fstatic-upload%2Flogo-auth.png&issuer=eMAG&secret=NFUQYTMH6UBEBG425XDYAMTG4RC3FEAULVVIM4NRBEXCMZWYRZEY5DKIHGG7ZY7MA2Y7EUV7FEEJSFAX3T5IFSALXHPQIQVGNLOCVLQ
