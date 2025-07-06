# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：images.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024-12-19 21:52 
-------------------------------------
'''
from loguru import logger
from sanic import Blueprint, json, Request,response

from apps.images.tool import get_image_source_img_file, binary_image_to_thumbnail, image_id_to_url
from apps.user.tool import get_user_campany_id_by_request
from config.bean import SuccessResponse, FailureResponse
from config.constant import IMAGE_BASE_URL
from models.images import Images
from mongodb_tool.db_list import mongodb_list, get_request_base_params, mongodb_create, mongodb_update
from utils.auth import protected
from utils.common import get_hash, get_uuid

bp_images = Blueprint("images", url_prefix="images")  # 创建蓝图


@bp_images.get("/get/<img_id>")
async def images_show(request: Request,img_id:str):
    """
    :param img_id:
    :param request:
    :return:
    """
    return await get_image_source_img_file(source_id=img_id)


@bp_images.post("/upload")
@protected(permission=[])
async def images_upload(request: Request):
    """
    :param request:
    :return:
    """
    campany_id = await get_user_campany_id_by_request(request)
    sourceId = get_uuid()
    emUrl = None
    sourceImgFile = request.files['file'][0].body
    thumbImgFile = binary_image_to_thumbnail(sourceImgFile)
    is_ok, msg = await mongodb_create(collection_name=Images.collection_name, data={
        "campanyId":campany_id,
        "sourceId":sourceId,
        "emUrl":emUrl,
        "sourceImgFile":sourceImgFile,
        "thumbImgFile":thumbImgFile
    }, uni_field=["campanyId","sourceId"])
    if is_ok:
        return json(**SuccessResponse(message=msg, data={"url":image_id_to_url(sourceId)}).to_response())
    else:
        return json(**FailureResponse(message=msg, data={}).to_response())
