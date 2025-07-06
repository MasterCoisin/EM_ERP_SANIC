# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：otpManager.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-03-29 14:36 
-------------------------------------
'''
import pyotp
#otpauth://totp/eMAG%3A1165621218%40qq.com?image=https%3A%2F%2Fs13emagst.akamaized.net%2Flayout%2Fro%2Fstatic-upload%2Flogo-auth.png&issuer=eMAG&secret=K4EWBVKLYRUX4UWHGET5DM2TU7DQOU4A7ANQZC37JI6DZKA76ANDRDBVMU6VUJS4ZT23DIYZSEAACHX4DQRUITOM57LLEIHQV2MCQ5Y
"""otpauth://totp/eMAG%3A2849068933%40qq.com?image=https%3A%2F%2Fs13emagst.akamaized.net%2Flayout%2Fro%2Fstatic-upload%2Flogo-auth.png&issuer=eMAG&secret=CW3Q6I7ANR5BZZD72UY2OQOOOSGW3TBVFHR5NBM3XIUKHWV4V4TZV5L37FG634SOUDHH7KIF6PXF7XHEFPZL4XO2LYWJNZ6SX3FG5OA"""

"""
def otp_create(otpKey):
    # 创建 TOTP 对象，使用 base32 编码的密钥
    totp = pyotp.TOTP(otpKey)

    # 获取当前时间的 OTP
    return totp.now()  # 输出示例：'492039'"""


def otp_creat1e():
    # 创建 TOTP 对象，使用 base32 编码的密钥
    totp = pyotp.TOTP(
        'CW3Q6I7ANR5BZZD72UY2OQOOOSGW3TBVFHR5NBM3XIUKHWV4V4TZV5L37FG634SOUDHH7KIF6PXF7XHEFPZL4XO2LYWJNZ6SX3FG5OA')

    # 获取当前时间的 OTP
    print(totp.now())  # 输出示例：'492039'

otp_creat1e()
def otp_create(otpKey):
    # 创建 TOTP 对象，使用 base32 编码的密钥
    totp = pyotp.TOTP(otpKey)

    # 获取当前时间的 OTP
    return totp.now()
