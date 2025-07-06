# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：tool.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-02-11 16:53 
-------------------------------------
'''
from io import BytesIO

import aiohttp
from PIL import Image, ImageOps
from motor.motor_asyncio import AsyncIOMotorCollection
from sanic import Sanic, response

from config.constant import APP_NAME, IMAGE_BASE_URL
from models.images import Images

app = Sanic.get_app(APP_NAME)


def binary_image_to_thumbnail(binary_data):
    # 将二进制数据读取为图像
    img_file = BytesIO(binary_data)
    image = Image.open(img_file)

    # 校正EXIF方向
    image = ImageOps.exif_transpose(image)

    # 生成缩略图，最长边为300像素
    image.thumbnail((300, 300))
    try:
        # 确定输出格式，处理图像模式
        output_format = image.format.upper() if image.format else 'JPEG'
        if output_format in ('JPEG', 'JPG'):
            if image.mode != 'RGB':
                image = image.convert('RGB')
        elif output_format == 'PNG' and image.mode == 'P':
            image = image.convert('RGB')
    except:
        pass

    # 保存到二进制流
    output = BytesIO()
    image.save(output, format='JPEG')
    return output.getvalue()


async def get_image_source_img_file(source_id):
    collection: AsyncIOMotorCollection = app.ctx.mongo[Images.collection_name]
    # result = await collection.find_one({"sourceId": source_id})
    # if result.get("emUrl",None):
    #     return response.redirect(to=result.get("emUrl",None))
    result = await collection.find_one({"sourceId": source_id}, {"sourceImgFile": 1, "thumbImgFile": 1})

    return response.raw(
        result.get("sourceImgFile", None),
        # result.get("thumbImgFile", None) if result.get("thumbImgFile", None) else result.get("sourceImgFile", None),
        content_type="image/jpeg",  # 明确指定 JPEG 类型
        headers={"Content-Disposition": f"inline; filename={source_id}.jpg"}
    )


async def get_image_source_img_file_by_url_or_source_id(source_id):
    collection: AsyncIOMotorCollection = app.ctx.mongo[Images.collection_name]
    if "marketplace-static" not in source_id:
        result = await collection.find_one({"sourceId": source_id}, {"thumbImgFile": 1})
        return result.get("thumbImgFile", None)
    else:
        result = await collection.find_one({"emUrl": source_id}, {"thumbImgFile": 1})
        if result:
            return result.get("thumbImgFile", None)
        else:
            return None

async def get_image_emUrl(source_id):
    collection: AsyncIOMotorCollection = app.ctx.mongo[Images.collection_name]
    # result = await collection.find_one({"sourceId": source_id})
    # if result.get("emUrl",None):
    #     return response.redirect(to=result.get("emUrl",None))
    result = await collection.find_one({"sourceId": source_id}, {"emUrl": 1})

    return result.get("emUrl", None)


def url_to_id(imades: list):
    return [i.split("/")[-1] if 'fzwala.com' in i else i for i in imades]


def image_id_to_url(image_id):
    return f"{IMAGE_BASE_URL}{image_id}" if "http" not in image_id else image_id  # ('fzwala.com' not in image_id or ("http" in image_id and "https" not in image_id)) else image_id
