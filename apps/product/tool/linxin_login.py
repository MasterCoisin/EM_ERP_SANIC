# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：linxin_login.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-07-06 12:04 
-------------------------------------
'''
import base64

import requests
import json
from Crypto.Cipher import AES
from Crypto.Util.number import *
from Crypto.Util.strxor import *
from Crypto.Util.Padding import pad
#
ACCOUNT = "baitai-350000"
PWD = 'Lx159357'
# ACCOUNT = "13391234626bt"
# PWD = '0JUER4'


def get_login_secretkey():
    url = "https://gw.lingxingerp.com/newadmin/api/passport/getLoginSecretKey"

    payload = {}
    headers = {
        'authority': 'gw.lingxingerp.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'auth-token': '',
        'cache-control': 'no-cache',
        'content-length': '0',
        'origin': 'https://erp.lingxing.com',
        'pragma': 'no-cache',
        'referer': 'https://erp.lingxing.com/',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'x-ak-company-id': '901217529031491584',
        'x-ak-request-id': '5abadf08-a70b-4e53-892a-7f5b0aacef8f',
        'x-ak-request-source': 'erp',
        'x-ak-version': '1.0.0.0.0.200',
        'x-ak-zid': ''
    }

    response = requests.request("POST", url, headers=headers, data=payload).json()
    print(response)
    return response['data']


def utf8_parse(s):
    # 将字符串转换成字节流
    b = s.encode('utf-8')
    # 计算 WordArray 的长度（以 32 位整数为单位）
    length = (len(b) + 3) // 4
    # 初始化 WordArray 的内容为 0
    words = [0] * length
    # 将字节流中的每个字节存储到 WordArray 中
    for i in range(len(b)):
        word_index = i // 4
        byte_index = i % 4
        words[word_index] |= b[i] << (24 - byte_index * 8)
    # 创建 WordArray 对象并返回
    # print(words)
    return words


def get_key(old_key):
    key_list = utf8_parse(old_key)
    key_list_bate = [long_to_bytes(i) for i in key_list]
    # print(key_list_bate)
    new_key = bytearray()
    for i in key_list_bate:
        new_key.extend(i)
    # print(new_key)
    return new_key


def encrypt_aes(plaintext, key):
    cipher = AES.new(key.encode(), AES.MODE_ECB)
    padded_plaintext = plaintext + (AES.block_size - len(plaintext) % AES.block_size) * chr(AES.block_size - len(plaintext) % AES.block_size)
    ciphertext = cipher.encrypt(padded_plaintext.encode())
    return base64.b64encode(ciphertext).decode()


def login(pwd,secretId):
    headers = {
        'authority': 'gw.lingxingerp.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'auth-token': '',
        'cache-control': 'no-cache',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://erp.lingxing.com',
        'pragma': 'no-cache',
        'referer': 'https://erp.lingxing.com/',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'x-ak-request-id': 'cf27b2fa-34b3-4955-aca4-8b79f8a8eff7',
        'x-ak-request-source': 'erp',
        'x-ak-version': '1.0.0.0.0.200',
        'x-ak-zid': '',
    }

    json_data = {
        'account': ACCOUNT,
        'pwd': pwd,
        'verify_code': '',
        'uuid': '254cd273-7e74-4f22-ba3e-ae199adbff19',
        'auto_login': 1,
        # 'randStr': '@ywL',
        # 'ticket': 't03hPBBq3jECZDNi0KLbw71udaHFI0LKOu8CMO75Jz4Dd16-8FlGsO6aDfXMLND3mixktpRm4DgpHAxeVIvvWY6dFcZycj0MRd_okhxHlslv_dFfPY6ShZD1w**',
        'sensorsAnonymousId': '18725ea3f9fd58-07aaf295e0ad0dc-26021151-1764000-18725ea3fa0804',
        'secretId': secretId,
    }

    response = requests.post('https://gw.lingxingerp.com/newadmin/api/passport/login', headers=headers, json=json_data).json()
    return response
    # Note: json_data will not be serialized by requests
    # exactly as it was in the original request.
    # data = '{"account":"13391234626bt","pwd":"7yyFicrO19pT3btePmIDCA==","verify_code":"","uuid":"254cd273-7e74-4f22-ba3e-ae199adbff19","auto_login":1,"randStr":"@ywL","ticket":"t03hPBBq3jECZDNi0KLbw71udaHFI0LKOu8CMO75Jz4Dd16-8FlGsO6aDfXMLND3mixktpRm4DgpHAxeVIvvWY6dFcZycj0MRd_okhxHlslv_dFfPY6ShZD1w**","sensorsAnonymousId":"18725ea3f9fd58-07aaf295e0ad0dc-26021151-1764000-18725ea3fa0804","secretId":"d860457fcea740018127082e56df1c4e"}'
    # response = requests.post('https://gw.lingxingerp.com/newadmin/api/passport/login', headers=headers, data=data)


def run():
    login_secretkey = get_login_secretkey()
    # print(login_secretkey)
    key = login_secretkey['secretKey']
    secretId = login_secretkey['secretId']
    # key = 'mVTZ8pXTQXsEBwFw'.encode('utf-8')
    data = PWD
    pwd = encrypt_aes(data,key)
    # print(pwd)
    res = login(pwd,secretId)
    # print(res)
    return res['token']


def api_get_ad_code():
    headers = {
        "Host": "gw.lingxingerp.com",
        "Connection": "keep-alive",
        "X-AK-Company-Id": "901217529031491584",
        "sec-ch-ua-platform": "\"Windows\"",
        "X-AK-Version": "3.5.9.3.0.176",
        "X-AK-Uid": "10431785",
        "sec-ch-ua": "\"Google Chrome\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
        "auth-token": run(),
        "X-AK-Language": "zh",
        "sec-ch-ua-mobile": "?0",
        "X-AK-Request-Id": "a81e9a6a-7c21-43cf-a303-25173f4fce22",
        "X-AK-Request-Source": "erp",
        "Accept": "application/json, text/plain, */*",
        "X-AK-Zid": "10330128",
        "X-AK-PLATFORM": "1",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F70 Safari/600.1.4",
        "AK-Client-Type": "web",
        "AK-Origin": "https://erp.lingxing.com",
        "X-AK-ENV-KEY": "SAAS-101",
        "Origin": "https://erp.lingxing.com",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://erp.lingxing.com/",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    url = "https://gw.lingxingerp.com/newadmin/oauth/adver"
    params = {
        "req_time_sequence": "%/newadmin%/oauth%/adver$$1"
    }
    response = requests.get(url, headers=headers, params=params)

    return response.json()['data']


def api_ad_login(login_url):
    headers = {
        "Host": "ads.lingxing.com",
        "Connection": "keep-alive",
        "sec-ch-ua": "\"Google Chrome\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F70 Safari/600.1.4",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://erp.lingxing.com/",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    cookies = {
        # "seller-auth-erp-url": "https%%3A%%2F%%2Ferp.lingxing.com%%2Fapi%%2Fseller%%2FoauthRedirect",
        # "sensorsdata2015jssdkchannel": "%%7B%%22prop%%22%%3A%%7B%%22_sa_channel_landing_url%%22%%3A%%22%%22%%7D%%7D",
        # "_ga": "GA1.1.822244663.1726048319",
        # "_ga_57W1QW8BJG": "GS1.1.1726048319.1.0.1726048320.0.0.0",
        # "sensorsdata2015jssdkcross": "%%7B%%22distinct_id%%22%%3A%%2210330128-10330128%%22%%2C%%22first_id%%22%%3A%%2218725ea3f9fd58-07aaf295e0ad0dc-26021151-1764000-18725ea3fa0804%%22%%2C%%22props%%22%%3A%%7B%%7D%%2C%%22identities%%22%%3A%%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTg3MjVlYTNmOWZkNTgtMDdhYWYyOTVlMGFkMGRjLTI2MDIxMTUxLTE3NjQwMDAtMTg3MjVlYTNmYTA4MDQiLCIkaWRlbnRpdHlfbG9naW5faWQiOiIxMDMzMDEyOC0xMDMzMDEyOCJ9%%22%%2C%%22history_login_id%%22%%3A%%7B%%22name%%22%%3A%%22%%24identity_login_id%%22%%2C%%22value%%22%%3A%%2210330128-10330128%%22%%7D%%2C%%22%%24device_id%%22%%3A%%2218725ea3f9fd58-07aaf295e0ad0dc-26021151-1764000-18725ea3fa0804%%22%%7D",
        # "Hm_lvt_ff7ba94465b63374a6a2cba75ead583e": "1729147653,1729159761,1729223494",
        # "_gcl_au": "1.1.511706139.1744622284",
        # "Hm_lvt_49f9312a5d99eba61237ede945a266af": "1746507115",
        # "sensor-distinace-id": "10330128-10330128"
    }
    response = requests.get(login_url, headers=headers, cookies=cookies)

    return response


def get_ad_token():
    ad_login_url = api_get_ad_code()
    response = api_ad_login(login_url=ad_login_url)

    return response.cookies.get_dict()['amzbi']


if __name__ == '__main__':
    print(run())