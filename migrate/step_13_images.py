# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：step_1_images.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：迁移images表
@Date        ：2024-12-19 21:16 
-------------------------------------
'''
from PIL import Image, ImageOps
from io import BytesIO
import requests
from loguru import logger
from concurrent.futures import ThreadPoolExecutor
from mongoengine import *
from tqdm import tqdm

from migrate.constant import CAMPANY_ID
from utils.common import to_mongo
from utils.models import ModelManagerOld as ModelManager

class Images(DynamicDocument):
    sourceId = StringField()
    emUrl = StringField()
    sourceImgFile = BinaryField()
    thumbImgFile = BinaryField()
    meta = {
        'db_alias': 'new_db',
        'collection': 'images',
        "indexes": [
            {
                'fields': ['sourceId'],
                "name": "sourceId"
            }
        ]
    }


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
    image.save(output,format='JPEG')
    return output.getvalue()


def download_img(url):
    try:
        payload = {}
        headers = {
            'authority': 'mnks.jxedt.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'cookie': 'id58=CpQQYGVURiFZ60T2B6yZAg==; 58tj_uuid=725838b5-9f4c-481d-941d-4496598cddcc; als=0; Hm_lvt_6be941daec905c6555161e79e92067b2=1700021794; Hm_lvt_e43feb296c32a4add052b7249ed6bf2b=1700021798; Hm_lvt_b54f0f8b3b75a8b7486c9adedf28f361=1700021809; local_car_flag=undefined; jxedt_dialog_time=41879066; carText=%E5%B0%8F%E8%BD%A6; local_city=%E5%85%A8%E5%9B%BD; local_city_pingying=%2F; init_refer=https%253A%252F%252Fwww.baidu.com%252Flink%253Furl%253D1eBygKDDySWxf2p0zdmrWYlNfXZxNTp_Y_EgdGHV_1i%2526wd%253D%2526eqid%253Dc775474200011b580000000665544618; new_uv=3; Hm_lpvt_6be941daec905c6555161e79e92067b2=1700027575; new_session=0; Hm_lpvt_b54f0f8b3b75a8b7486c9adedf28f361=1700027580; Hm_lpvt_e43feb296c32a4add052b7249ed6bf2b=1700027582',
            'pragma': 'no-cache',
            'referer': 'https://mnks.jxedt.com/ckm1/sxlx/',
            'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }

        response = requests.request("GET", url, headers=headers, data=payload,proxies={"http":"http://127.0.0.1:10809","https":"http://127.0.0.1:10809"}).content
        return response
    except:
        print(url)

def task(obj):
    try:
        if Images.objects(sourceId=obj.source_id).first():return
        adds = []
        img_binary = download_img(obj.url)
        adds.append({
            "campanyId": CAMPANY_ID,
            "sourceId": obj.source_id,
            "emUrl": obj.url,
            "sourceImgFile": img_binary,
            "thumbImgFile": binary_image_to_thumbnail(img_binary)
        })
        to_mongo(Images, adds, ["campanyId","sourceId"])
        obj.trans = True
        logger.info(f"success {obj.source_id}")
    except:
        pass
def main():
    Images.objects().count()
    data = old_images_model.objects()
    pool = ThreadPoolExecutor(50)
    for obj in tqdm(data):
        pool.submit(task,obj)
    pool.shutdown(wait=True)


if __name__ == '__main__':
    connect(host="mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin", alias='new_db')
    old_images_model = ModelManager.get_model("image_to_em_link", "base")
    main()
