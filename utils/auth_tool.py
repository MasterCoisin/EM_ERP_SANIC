# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：auth_tool.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-03-31 21:13 
-------------------------------------
'''
import jwt

def get_openid_from_token(request):
    if not request.token:
        return None
    try:
        payload = jwt.decode(
            request.token, request.app.config.SECRET, algorithms=["HS256"]
        )
        # 验证是否过期
        return payload.get("identity", None)
    except jwt.exceptions.InvalidTokenError:
        return None