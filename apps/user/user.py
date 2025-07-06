# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：login.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：登录模块
@Date        ：2024-11-17 18:45 
-------------------------------------
'''
from loguru import logger
from sanic import Blueprint, json, Request

from apps.campany.tool import get_campany_info_by_name, create_campany_info, get_campany_info_by_id, init_campany_data
from apps.user.tool import check_user_in_db, get_user_info_in_db, check_user_in_db_by_phone_and_password, \
    check_user_in_db_by_phone, get_user_campany_id_by_request, is_valid_phone_number
from config.bean import SuccessResponse, UnauthorizedResponse, FailureResponse
from config.constant import EXPIRES_DELTA, DEFAULT_PASSWORD
from cores.access_token_manager import get_user_info
from models.sys_user import SysUser
from mongodb_tool.db_list import mongodb_create, mongodb_update, get_request_base_params, mongodb_list
from utils.auth import create_access_token, protected, user_permission
from utils.auth_tool import get_openid_from_token
from utils.common import get_uuid, args_valid
from utils.format_tool import str_to_md5
from utils.mongo_tool import add_filter_in_filters

bp_user = Blueprint("user", url_prefix="user")  # 创建蓝图


@bp_user.post("/login")
async def login(request):
    """
    用户登录
    :param request:
    :return:
    """
    code = request.json.get('code', None)  # 飞书code
    if not code:
        return json(**UnauthorizedResponse(message="登陆失败").to_response())
    user_info = await get_user_info(code)
    if not user_info:
        return json(**UnauthorizedResponse(message="登陆失败").to_response())
    document = await check_user_in_db(user_info)
    if not document.get("deleted", False):
        access_token = create_access_token(identity=user_info["open_id"], expires_delta=EXPIRES_DELTA)  # 设置过期时间
        return json(**SuccessResponse(message="登陆成功", data={"access_token": access_token}).to_response())
    return json(**FailureResponse(message="请联系管理员激活账号", data={}).to_response())


@bp_user.post("/loginByPhone")
async def login_by_phone(request):
    """
    用户登录
    :param request:
    :return:
    """
    phone = request.json.get('phone', None)
    password = request.json.get('password', None)
    if not phone or not password:
        return json(**UnauthorizedResponse(message="请输入用户名或密码").to_response())
    document = await check_user_in_db_by_phone_and_password(phone, str_to_md5(password))
    if not document:
        return json(**UnauthorizedResponse(message="账号或密码错误").to_response())
    if not document.get("deleted", False):
        access_token = create_access_token(identity=document["open_id"], expires_delta=EXPIRES_DELTA)  # 设置过期时间
        return json(**SuccessResponse(message="登陆成功", data={"access_token": access_token}).to_response())
    return json(**FailureResponse(message="请联系管理员激活账号", data={}).to_response())


@bp_user.get("/getLoginUserPermissions")
@protected()
async def get_login_user_permissions(request):
    """
    获取用户信息
    :param request:
    :return:
    """
    openid = get_openid_from_token(request)
    return json(
        **SuccessResponse(message="OK",
                          data=await user_permission.get_user_permission(open_id=openid)).to_response())


@bp_user.get("/home")
@protected()
async def user_home_get(request):
    """
    获取用户信息
    :param request:
    :return:
    """
    open_id = get_openid_from_token(request)
    data = await get_user_info_in_db(open_id=open_id)
    res = {k: data.get(k, None) for k in ['avatar_url', 'name', 'mobile', 'open_id','campanyId']}
    campany_info = await get_campany_info_by_id(campanyId=res.get("campanyId",None))
    res["campanyName"] = campany_info.get("campanyName",None)
    res["isVip"] = campany_info.get("isVip",None)
    res["isSvip"] = campany_info.get("isSvip", None)
    res["expireTime"] = campany_info.get("expireTime", None)
    return json(**SuccessResponse(message="OK", data=res).to_response())


@bp_user.post("/changePassword")
@protected()
async def user_change_password(request):
    """
    :param request:
    :return:
    """
    open_id = get_openid_from_token(request)
    new_password = request.json.get("new_password", None)
    if not new_password:
        return json(**FailureResponse(message="请输入新密码", data={}).to_response())
    is_ok, msg = await mongodb_update(collection_name=SysUser.collection_name,
                                      data={"open_id": open_id, "password": str_to_md5(new_password)},
                                      uni_field=["open_id"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_user.post("/list")
@protected(permission=["userManager:list"])
async def user_list(request: Request):
    """
    查询店铺列表
    :param request:
    :return:
    """
    current_page, page_size, fields, filters, sorts = get_request_base_params(request)
    campany_id = await get_user_campany_id_by_request(request)
    filters = add_filter_in_filters(filters, "campanyId", campany_id)
    print(filters)
    data = await mongodb_list(collection_name=SysUser.collection_name, fields=fields, filters=filters, sorts=sorts,
                              current_page=current_page, page_size=page_size)
    return json(**SuccessResponse(message="OK", data=data).to_response())


@bp_user.post("/create")
@protected(permission=["userManager:create"])
async def user_create(request: Request):
    """
    创建用户
    :param request:
    :return:
    """
    data: dict = request.json
    campany_id = await get_user_campany_id_by_request(request)
    # 自定义open_id
    data["open_id"] = f"erp-{get_uuid()}"
    data["password"] = str_to_md5(DEFAULT_PASSWORD)
    data["campanyId"] = campany_id
    is_ok, msg = await mongodb_create(collection_name=SysUser.collection_name, data=data, uni_field=["open_id","campanyId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_user.post("/createByCampany")
async def user_create_by_campany(request: Request):
    """
    创建用户
    :param request:
    :return:
    """
    data: dict = request.json
    campany_name = data.get("campanyName", None)
    phone = data.get("phone", None)
    password = data.get("password", None)
    if not args_valid([campany_name, phone, password]):
        return json(**FailureResponse(message="参数不完整", data={}).to_response())
    campany_name = campany_name.strip()
    if campany_name.strip()=="":
        return json(**FailureResponse(message="公司名字不能为空", data={}).to_response())
    if not is_valid_phone_number(phone.strip()):
        return json(**FailureResponse(message="手机号格式错误", data={}).to_response())
    if len(password.strip())<6:
        return json(**FailureResponse(message="密码至少为6位字符", data={}).to_response())
    campany_info = await get_campany_info_by_name(campanyName=campany_name)
    if campany_info:
        return json(**FailureResponse(message="该公司已注册", data={}).to_response())
    if await check_user_in_db_by_phone(phone=phone):
        return json(**FailureResponse(message="该手机号已注册过", data={}).to_response())
    # 自定义open_id
    campany_info = await create_campany_info(campanyName=campany_name)
    campany_id = campany_info.get("campanyId", None)
    # TODO 初始化,新公司注册后初始化数据库
    await init_campany_data(campany_id)
    #
    add = {
        "mobile": phone,
        "open_id": f"erp-{get_uuid()}",
        "password": str_to_md5(password.strip()),
        "campanyId": campany_info.get("campanyId", None),
        "is_super_user":True,
        "is_sys_super_user": False,
        "deleted": False
    }
    is_ok, msg = await mongodb_create(collection_name=SysUser.collection_name, data=add, uni_field=["open_id"])
    if is_ok:
        return json(**SuccessResponse(message="注册完成，请联系客服激活", data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())


@bp_user.post("/update")
@protected(permission=["userManager:update"])
async def user_update(request: Request):
    """
    更新用户信息
    :param request:
    :return:
    """
    data: dict = request.json
    _id = data.get("id", None)
    id_field = data.get("id_field", "open_id")
    campany_id = await get_user_campany_id_by_request(request)
    update_data = data.get("data", {})
    update_data[id_field] = _id
    update_data["campanyId"] = campany_id
    is_ok, msg = await mongodb_update(collection_name=SysUser.collection_name, data=update_data,
                                      uni_field=[id_field,"campanyId"])
    await user_permission.update_user_role(open_id=update_data.get("open_id"))
    if is_ok:
        return json(**SuccessResponse(message=msg, data={}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())
