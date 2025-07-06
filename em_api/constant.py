# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BACKEN 
@File        ：constant.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024-04-30 11:56 
-------------------------------------
'''
import base64

username = '2849068933@qq.com'
password = 'LEJAjCG'
HASH = base64.b64encode((username + ':' + password).encode()).decode()