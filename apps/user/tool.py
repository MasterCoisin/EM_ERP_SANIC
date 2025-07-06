# -*- coding: UTF-8 -*-
"""
@Project     ：EM_ERP_BAKEN_SANIC
@File        ：toold.py
@IDE         ：PyCharm
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024-11-17 22:59
-------------------------------------
"""
from sanic import Sanic
from config.constant import APP_NAME
from models.sys_user import SysUser
from utils.auth_tool import get_openid_from_token
import re

app = Sanic.get_app(APP_NAME)


def is_valid_phone_number(phone_number):
    # 定义手机号码的正则表达式模式
    pattern = r'^1[3-9]\d{9}$'
    # 使用 re.match 方法检查手机号码是否匹配模式
    if re.match(pattern, phone_number):
        return True
    return False

async def check_user_in_db(user_info: dict) -> dict:
    """
    检查用户是否在数据库，在的话更新数据，不在的话添加用户
    :param user_info: 用户信息
    :return: None
    """
    user_info["deleted"] = False
    document = await app.ctx.mongo[SysUser.collection_name].find_one({"open_id": {"$eq": user_info.get("open_id")}})
    if not document:
        user_info["is_super_user"] = False
        await app.ctx.mongo[SysUser.collection_name].insert_one(user_info)
    else:
        await app.ctx.mongo[SysUser.collection_name].update_one({"open_id": user_info.get("open_id")},
                                                                {"$set": {k: user_info.get(k, None) for k in
                                                                          ["open_id", "name", "en_name", "tenant_key",
                                                                           "union_id", "user_id"]}})
    return await app.ctx.mongo[SysUser.collection_name].find_one({"open_id": {"$eq": user_info.get("open_id")}})


async def check_user_in_db_by_phone_and_password(phone, password):
    return await app.ctx.mongo[SysUser.collection_name].find_one(
        {"mobile": {"$eq": phone}, "password": {"$eq": password}})


async def check_user_in_db_by_phone(phone):
    return await app.ctx.mongo[SysUser.collection_name].find_one(
        {"mobile": {"$eq": phone}})


async def get_user_info_in_db(open_id: str) -> dict:
    """
    查询用户信息
    :param open_id:
    :param openid:
    :return:
    """
    document = await app.ctx.mongo[SysUser.collection_name].find_one({"open_id": {"$eq": open_id}})
    if not document:
        return {}
    else:
        return document


async def get_user_campany_id(open_id: str) -> None | str:
    """
    :param open_id:
    :param openid:
    :return:
    """
    document = await app.ctx.mongo[SysUser.collection_name].find_one({"open_id": {"$eq": open_id}}, {"campanyId": 1})
    if not document:
        return None
    else:
        return document.get("campanyId", None)


async def get_user_campany_id_by_request(request) -> None | str:
    """
    :return:
    """
    open_id = get_openid_from_token(request)
    return await get_user_campany_id(open_id)
