# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：auth.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024-11-17 19:06 
-------------------------------------
'''
from loguru import logger
from time import time
from functools import wraps

import jwt
from sanic import json, Sanic

from apps.campany.tool import get_campany_is_vip
from apps.user.tool import get_user_campany_id
from config.bean import UnauthorizedResponse, FailureResponse
from config.constant import APP_NAME
from models.button import Button
from models.menu import Menu
from models.role import Role
from models.route import Route
from models.sys_user import SysUser
from mongodb_tool.db_list import mongodb_list

app = Sanic.get_app(APP_NAME)


class RolePermission():
    """
    管理角色权限
    """

    def __init__(self):
        self.role_permission_info = {}

    def form_tree(self, data):
        node_dict = {}
        for item in data:
            parent_id = item["parentId"]
            tab_id = item["tabId"]
            title = item["title"]
            node_info = {"tabId": tab_id, "title": title,"free":item.get("free",True),"svip":item.get("svip",True),"vip":item.get("vip",True), "children": []}
            if parent_id is None:
                node_dict[tab_id] = node_info
        for item in data:
            parent_id = item["parentId"]
            tab_id = item["tabId"]
            title = item["title"]
            node_info = {"tabId": tab_id, "title": title,"free":item.get("free",True),"svip":item.get("svip",True),"vip":item.get("vip",True), "children": []}
            if parent_id is None:
                pass
            else:
                if parent_id not in node_dict:
                    node_dict[parent_id] = {"tabId": parent_id, "title": "","free":False,"isSvip":True,"isVip":True, "children": []}
                node_dict[parent_id]["children"].append(node_info)
        result = list(node_dict.values())
        return result

    async def load_data(self):
        route_data = await mongodb_list(collection_name=Route.collection_name, fields=[], filters=[{"field": 'deleted', "max": None, "min": None, "query": '', "t": 'eq', "value": False }], sorts=[],
                                        current_page=1, page_size=10000)
        button_data = await mongodb_list(collection_name=Button.collection_name, fields=["permission_code"], filters=[{"field": 'deleted', "max": None, "min": None, "query": '', "t": 'eq', "value": False }],
                                         sorts=[],
                                         current_page=1, page_size=10000)
        menu_data = await mongodb_list(collection_name=Menu.collection_name, fields=[], filters=[{"field": 'deleted', "max": None, "min": None, "query": '', "t": 'eq', "value": False }],
                                       sorts=[{"field": "priority", "t": "asc"}],
                                       current_page=1, page_size=10000)
        root_permissions_code = [i["permission_code"] for i in button_data["data"]]
        root_menus = self.form_tree(menu_data["data"])
        root_menus_without_sys = self.form_tree([i for i in menu_data["data"] if i["nodeId"] not in ["routeManager","menuManager","buttonManager","campanyManager","vipPriceManager","sassManager","couponManager"]])
        self.role_permission_info["super_sys_user"] = {"routers": route_data["data"],
                                                   "permissionsCode": root_permissions_code,
                                                   "menus": root_menus}
        # 企业级管理员删除路由权限
        self.role_permission_info["super_user"] = {"routers": [i for i in route_data["data"] if i["name"] not in ["routeManager","menuManager","buttonManager","campanyManager","vipPriceManager","sassManager","couponManager"]],
                                                       "permissionsCode": [i for i in root_permissions_code if i.split(":")[0] not in [ "routeManager","menuManager","buttonManager","campanyManager","vipPriceManager","sassManager","couponManager"]],
                                                       "menus": root_menus_without_sys}
        #
        role_datas = await mongodb_list(collection_name=Role.collection_name, fields=[], filters=[],
                                        sorts=[],
                                        current_page=1, page_size=10000)

        for role_data in role_datas["data"]:
            campany_id = role_data.get("campanyId")
            role_code = role_data.get("role_code")
            routers = [i for i in route_data["data"] if i["name"] in role_data.get("routers")]
            permissionsCode = role_data.get("permissionsCode")
            menus_ = role_data.get("menus")
            menu_codes = []
            for m in menus_:
                menu_codes += m.split("---")
            menu_codes = list(set(menu_codes))
            menus = self.form_tree([i for i in menu_data["data"] if i["tabId"] in menu_codes])
            if campany_id not in self.role_permission_info:
                self.role_permission_info[campany_id] = {}
            self.role_permission_info[campany_id][role_code] = {"routers": routers, "permissionsCode": permissionsCode,
                                                    "menus": menus}

    async def get_role_permission(self, role,campany_id):
        print(role,campany_id,self.role_permission_info)
        logger.info(f"role:{role}")
        if role in ["super_user","super_sys_user"]:
            if role not in self.role_permission_info:
                await role_permission.load_data()
            return self.role_permission_info.get(role, {"routers": [], "permissionsCode": [], "menus": []})
        if role not in self.role_permission_info.get(campany_id,{}):
            await role_permission.load_data()
        return self.role_permission_info.get(campany_id,{}).get(role, {"routers": [], "permissionsCode": [], "menus": []})


role_permission = RolePermission()


class UserPermission():
    """
    管理用户权限
    """

    def __init__(self):
        self.user_info = {}  # {"open_id":{"is_super_user":True,"role":[]}}

    async def get_user_role(self, open_id) -> dict:
        """
        获取用户角色
        :param open_id:
        :return:
        """
        if open_id not in self.user_info:
            document = await app.ctx.mongo[SysUser.collection_name].find_one({"open_id": {"$eq": open_id}},
                                                                             {"_id": 0, "is_super_user": 1, "role": 1,"is_sys_super_user":1})

            if document:
                self.user_info[open_id] = {"is_super_user": document.get("is_super_user", False),
                                           "role": document.get("role", None) if document.get("role",
                                                                                              False) else None,"is_sys_super_user":document.get("is_sys_super_user", False)}
            else:
                self.user_info[open_id] = {"is_super_user": False, "role": None,"is_sys_super_user":False}
        return self.user_info[open_id]

    async def get_user_permission(self, open_id) -> dict:
        """
        返回用户路由 菜单 按钮权限
        :param open_id:
        :return:
        """
        user_role_info = await self.get_user_role(open_id)
        if user_role_info.get("is_super_user", False) and not user_role_info.get("is_sys_super_user", False):
            return await role_permission.get_role_permission("super_user",None)
        elif user_role_info.get("is_super_user", False) and user_role_info.get("is_sys_super_user", False):
            return await role_permission.get_role_permission("super_sys_user",None)
        role_info = await self.get_user_role(open_id=open_id)
        campany_id = await get_user_campany_id(open_id=open_id)
        if not role_info.get("role", None):
            return {}
        return await role_permission.get_role_permission(role_info.get("role", None),campany_id)

    async def update_user_role(self, open_id):
        """
        更新用户权限
        :param open_id:
        :return:
        """
        document = await app.ctx.mongo[SysUser.collection_name].find_one({"open_id": {"$eq": open_id}},
                                                                         {"_id": 0, "is_super_user": 1, "role": 1})
        if document:
            self.user_info[open_id] = {"is_super_user": document.get("is_super_user", False),
                                       "role": document.get("role", None) if document.get("role",
                                                                                          False) else None}
            logger.info(f"更新用户权限 {open_id} {self.user_info[open_id]}")
        else:
            self.user_info[open_id] = {"is_super_user": True, "role": None}


user_permission = UserPermission()


def check_token(request):
    if not request.token:
        return False, None

    try:
        payload = jwt.decode(
            request.token, request.app.config.SECRET, algorithms=["HS256"]
        )
        # 验证是否过期
        if payload.get("expire_time", None) and time() > payload.get("expire_time", None):
            return False, payload.get("identity", None)
    except jwt.exceptions.InvalidTokenError:
        return False, None
    else:
        return True, payload.get("identity", None)





async def check_permission(open_id, permission):
    user_p = await user_permission.get_user_permission(open_id=open_id)
    permission_has = user_p.get("permissionsCode", [])
    for i in permission:
        if i not in permission_has:
            return False
    return True


def protected(permission=None,needVip = False,needSvip=False,needSuper=False):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            is_authenticated, open_id = check_token(request)
            if is_authenticated:
                campany_id = await get_user_campany_id(open_id=open_id)
                is_vip, is_svip, is_super = await get_campany_is_vip(campanyId=campany_id)
                if needSuper and not is_super:
                    return json(**FailureResponse(message="无权限!").to_response())
                # 判断vip
                if needSvip:
                    if not is_svip:
                        if needVip:
                            if is_vip:
                                pass
                            else:
                                return json(**FailureResponse(message="请购买高级会员或者选品会员后使用!").to_response())
                        else:
                            return json(**FailureResponse(message="请购买高级会员后使用!").to_response())
                if not needSvip and needVip:
                    if needVip:
                        if is_vip:
                            pass
                        else:
                            return json(**FailureResponse(message="请购买选品会员后使用!").to_response())
                user_role = await user_permission.get_user_role(open_id)
                if user_role.get("is_super_user", False):
                    logger.info(f"open id:{open_id} is super user")
                    response = await f(request, *args, **kwargs)
                    return response
                if permission:
                    has_permission = await check_permission(open_id, permission)
                    if has_permission:
                        response = await f(request, *args, **kwargs)
                        return response
                    else:
                        return json(**FailureResponse (message="没有权限执行此操作!").to_response())
                else:
                    response = await f(request, *args, **kwargs)
                    return response
            else:
                return json(**UnauthorizedResponse(message="登陆失败").to_response())

        return decorated_function

    return decorator


def create_access_token(identity, expires_delta=None):
    return jwt.encode({"identity": identity, "expire_time": time() + expires_delta if expires_delta else expires_delta},
                      app.config.SECRET)
