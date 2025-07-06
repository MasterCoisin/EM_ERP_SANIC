# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：update_em_product_offer.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-03-15 1:43 
-------------------------------------
'''
from loguru import logger
from tqdm import tqdm

from apps.listing.tool import get_listing_by_ean, update_listing_by_ean
from cores.access_token_manager import AccessTokenManager
from em_api.product_offer import ProductOfferApi
from em_api.estimate import EstimateApi
import aiohttp
import aiofiles
import os
import mimetypes


async def upload_image(path):
    tenant_access_token = AccessTokenManager.app.shared_ctx.cache.get("app_access_token", None)
    url = "https://open.feishu.cn/open-apis/im/v1/images"

    # 异步读取文件内容
    async with aiofiles.open(path, 'rb') as f:
        file_content = await f.read()

    # 获取文件名和 MIME 类型
    filename = os.path.basename(path)
    content_type, _ = mimetypes.guess_type(path)
    if content_type is None:
        content_type = 'application/octet-stream'

    # 构建 multipart 表单数据
    form = aiohttp.FormData()
    form.add_field('image_type', 'message')
    form.add_field('image',
                   file_content,
                   filename=filename,
                   content_type=content_type)

    headers = {
        'Authorization': f'Bearer {tenant_access_token}',
    }

    # 发送异步 POST 请求
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=form) as response:
            try:
                response_json = await response.json()
                if response_json.get("code", -1) == 0:
                    return response_json.get("data", {}).get("image_key", None)
            except Exception as e:
                print(f"Error parsing response: {e}")
            return None

def update_value(data,key,country,value):
    if key not in data:
        data[key] = {
            "ro":None,
            "bg": None,
            "hu": None
        }
    data[key][country] = value

async def update(data,country,shop_hash):
    try:
        part_number_key = data["part_number_key"]  # PNK
        sale_price = data["sale_price"]
        category_id = data["category_id"]
        description = data["description"]
        title = data["name"]
        brand = data["brand"]
        ean = data["ean"][0]
        obj = await get_listing_by_ean(ean=ean)
        print(obj)
        if obj:
            em_attribute = obj.get("emAttribute",{})
            em_attribute["pnk"][country] = part_number_key
            em_attribute["salePrice"][country] = sale_price
            em_attribute["category"][country] = category_id
            em_attribute["title"][country] = title
            em_attribute["html"][country]= description
            em_attribute["brand"][country] = brand
            if not em_attribute["commission"][country]:
                resp = await EstimateApi.read(ean,country=country,shop_hash=shop_hash)
                if resp["code"] == 200 and resp.get("data", {}).get("value"):
                    em_attribute["commission"][country] = int(float(resp.get("data", {}).get(
                        "value")))

            em_sale_info = obj.get("emSaleInfo",{})
            update_value(em_sale_info,'buyButtonRank',country,data.get('buy_button_rank', None))
            update_value(em_sale_info,'stock',country,data.get('stock', None)[0].get("value", None))
            update_value(em_sale_info,'status',country,data.get('status', None))
            update_value(em_sale_info,'ownership',country,data.get('ownership', None))
            update_value(em_sale_info,'bestOfferSalePrice',country,data.get('best_offer_sale_price', None))
            update_value(em_sale_info,'salePrice',country,float(data.get('sale_price', None)) if data.get('sale_price', None) else data.get(
                    'sale_price', None))
            update_value(em_sale_info,'currency',country,data.get('currency', None))
            update_value(em_sale_info,'numberOfOffers',country,data.get('number_of_offers', None))
            update_value(em_sale_info,'geniusEligibility',country,data.get('genius_eligibility', None))
            print(2,obj)

            await update_listing_by_ean(ean=ean,data={"emAttribute":em_attribute,"emSaleInfo":em_sale_info})
        else:
            print(f"no ean : {ean}")
    except Exception as e:
        logger.exception(e)


async def updata_pnk_from_em(country,shop_hash):
    count = await ProductOfferApi.count(country=country,shop_hash=shop_hash)
    if count["isError"]:
        raise
    count = int(count["results"]["noOfItems"])
    for page in range(1, count // 100 + 2):
        product_data = await ProductOfferApi.read(current_page=page,language="ro",country=country,shop_hash=shop_hash)
        if product_data["isError"]:
            raise
        for product_info in tqdm(product_data["results"]):
            await update(product_info,country,shop_hash)


