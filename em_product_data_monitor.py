# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：em_product_data_monitor.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-04-14 17:37 
-------------------------------------
'''
import json
import time
import requests
from retrying import retry
from datetime import datetime, timedelta
from loguru import logger
from tqdm import tqdm

from em_api.product_offer import ProductOfferApi
from mini_server_core.em_product_data_monitor_core.update_listing import ListingUpdater
from utils.models import ModelManager
from concurrent.futures import ThreadPoolExecutor


@retry(stop_max_attempt_number=5, wait_random_min=1000, wait_random_max=2000)
def send_to_fei_shu(msg, url):
    if not url:
        return
    data = json.dumps({
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": f"跟卖情报->{datetime.today().strftime('%Y-%m-%d %H %M %S')}",
                    "content": msg
                }
            }
        }
    })
    resp = requests.post(url=url,
                         data=data)
    print(resp.json())
    time.sleep(1)


def deal_data(data: list, country, genmai_notice_type, genmai_notice_url):
    n = 0
    msg = []
    msg.append(
        [
            {
                "tag": "text",
                "text": f"站点 : {country}"
            }
        ]
    )
    for item in data:
        part_number_key = item.get("part_number_key", "")
        number_of_offers = item.get("number_of_offers", 0)
        buy_button_rank = item.get("buy_button_rank", 0)
        best_offer_sale_price = item.get("best_offer_sale_price", 0)
        currency = item.get("currency", "RON")
        sale_price = item.get("sale_price", "")
        if buy_button_rank != None and buy_button_rank > 1:
            n += 1
            msg.append(
                [
                    {
                        "tag": "text",
                        "text": f"\n************** 跟卖产品 {n} ***************"
                    }
                ]
            )
            msg.append(
                [
                    {
                        "tag": "a",
                        "text": f"PNK: {part_number_key}",
                        "href": f"https://www.emag.ro/-/pd/{part_number_key}"
                    }
                ]
            )
            msg.append(
                [
                    {
                        "tag": "text",
                        "text": f"购物车情况:{buy_button_rank}/{number_of_offers}\n我们后台定价:{sale_price}{currency}\n获得购物车需要的后台定价:低于{best_offer_sale_price}{currency}"
                    }
                ]
            )
    if n:
        if genmai_notice_type == "feishu":
            print(msg)
            send_to_fei_shu(msg, genmai_notice_url)


def task(country, shop_id, campany_id, shop_hash, genmai_notice_type, genmai_notice_url):
    logger.info(f"shop_id:{shop_id} country:{country}")
    count = ProductOfferApi.countNormal(shop_hash=shop_hash)
    if count["isError"]:
        raise
    print(count)
    pages = int(count["results"]["noOfPages"])
    results = []
    for page in tqdm(range(1, pages + 1)):
        time.sleep(1)
        product_data = ProductOfferApi.readNormal(shop_hash=shop_hash, current_page=page, language=country,
                                                  country=country)
        if product_data["isError"]:
            raise
        results += product_data["results"]
    eans = []
    if results:
        # 更新listing数据
        for item in results:
            ean = item.get("ean", [])[0]
            if 3 in [it.get("value", None) for it in item.get("validation_status", [])]:
                continue
            if ean not in eans:
                eans.append(item.get("ean", [])[0] if item.get("ean", []) else None)
            else:
                print(item.get("ean", [])[0] if item.get("ean", []) else None, item)
            # print(item.get("id", None),item.get("ean", [])[0] if item.get("ean", []) else None)
            ListingUpdater(product_baken_data=item, shop_id=shop_id, campany_id=campany_id, country=country,
                           shop_hash=shop_hash).update()
        print(len(eans), len(set(eans)))
        #
        deal_data(results, country, genmai_notice_type, genmai_notice_url)


def task_main(shop_id, campany_id, shop_hash, genmai_notice_type, genmai_notice_url):
    for country in ["ro", "bg", "hu"]:  # "ro",, "bg", "hu"
        try:
            task(country, shop_id, campany_id, shop_hash, genmai_notice_type, genmai_notice_url)
        except Exception as e:
            logger.exception(e)


def main():
    pool = ThreadPoolExecutor(10)
    while True:
        shop_objs = shop_model.objects(em_login_info__hash__ne=None).only("shop_id", "campanyId",
                                                                                        "em_login_info",
                                                                                        "noticeUrls")
        for shop_obj in shop_objs:
            shop_id = shop_obj.shop_id
            campany_id = shop_obj.campanyId
            if not campany_model.objects(campanyId=campany_id, isSvip=True).first():
                continue
            shop_hash = shop_obj.em_login_info.get("hash", None)
            genmai_notice_info = shop_obj.noticeUrls.get("genmaiNotice", {})
            genmai_notice_type = genmai_notice_info.get("type", None)
            genmai_notice_url = genmai_notice_info.get("url", None)
            genmai_notice_open = genmai_notice_info.get("open", False)
            if not genmai_notice_open:
                continue
            if shop_hash:  # and genmai_notice_type and genmai_notice_url:
                task_main(shop_id, campany_id, shop_hash, genmai_notice_type, genmai_notice_url)
                # pool.submit(task_main, shop_id, campany_id, shop_hash, genmai_notice_type, genmai_notice_url)
        time.sleep(60 * 30)
    pool.shutdown(wait=True)


if __name__ == '__main__':
    campany_model = ModelManager.get_model("campany", "base")
    shop_model = ModelManager.get_model("shop", "base")
    em_orders_monitor_log_model = ModelManager.get_model("em_orders_monitor_log", "base")
    main()
