# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：order_monitor_main.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-04-12 19:42 
-------------------------------------
'''
import json
import time
import requests
from loguru import logger
from retrying import retry
from datetime import datetime, timedelta

from tqdm import tqdm

from utils.format_tool import str_to_datetime
from utils.models import ModelManager
from concurrent.futures import ThreadPoolExecutor
from em_api.order import OrderApi
from utils.common import to_mongo, cal_order_total_pcost


def get_last_date(days):
    current_time = datetime.now()
    two_minutes_ago = current_time - timedelta(minutes=60 * 24 * days)
    return two_minutes_ago.strftime('%Y-%m-%d %H:%M:%S')


def get_modified_before(modifiedAfter):
    if not modifiedAfter:
        return None
    # 1. 将字符串解析为时间对象
    input_time = datetime.strptime(modifiedAfter, "%Y-%m-%d %H:%M:%S")
    # 2. 计算20天后的时间
    future_time = input_time + timedelta(days=20)
    # 3. 转换为目标格式的字符串
    output_str = future_time.strftime("%Y-%m-%d %H:%M:%S")
    return output_str


def get_today():
    return datetime.today().strftime("%Y-%m-%d")

def date_add_1_s(original_time_str):
    original_time = datetime.strptime(original_time_str, '%Y-%m-%d %H:%M:%S')
    new_time = original_time + timedelta(seconds=1)
    new_time_str = new_time.strftime('%Y-%m-%d %H:%M:%S')
    return new_time_str
def parse_order(order):
    msg = []
    order_id = order.get("orderId", None)  # 订单id
    msg.append(
        [
            {
                "tag": "text",
                "text": f"订单号: {order_id}"
            }
        ]
    )
    status = order_status.get(order.get("status", None), "未知状态")  # 订单状态
    msg.append(
        [
            {
                "tag": "text",
                "text": f"订单状态: {status}"
            }
        ]
    )
    date = order.get("date", None)  # 订单日期
    msg.append(
        [
            {
                "tag": "text",
                "text": f"订单时间(罗马时区): {date}"
            }
        ]
    )
    payment_mode = order.get("payment_mode", None)  # 支付方式
    msg.append(
        [
            {
                "tag": "text",
                "text": f"支付方式: {payment_mode}"
            }
        ]
    )
    delivery_mode = order.get("delivery_mode", None)  # 交付方式
    msg.append(
        [
            {
                "tag": "text",
                "text": f"交付方式: {delivery_mode}"
            }
        ]
    )
    payment_status = payment_status_dict.get(order.get("payment_status", None), None)  # 支付状态
    msg.append(
        [
            {
                "tag": "text",
                "text": f"支付状态: {payment_status}"
            }
        ]
    )
    customer = order.get("customer", {})
    customer_name = customer.get("name", None)  # 客户姓名
    msg.append(
        [
            {
                "tag": "text",
                "text": f"客户姓名: {customer_name}"
            }
        ]
    )
    products = order.get("products", [])
    msg.append(
        [
            {
                "tag": "text",
                "text": f"购买产品列表"
            }
        ]
    )
    msg.append(
        [
            {
                "tag": "text",
                "text": f"---------------------"
            }
        ]
    )
    for product in products:
        msg += parse_product(product)
    return msg


def parse_product(product):
    msg = []
    part_number_key = product.get("part_number_key", None)  # 零件号
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
                "text": f"标题: {product.get('name')}"
            }
        ]
    )
    currency = product.get("currency", None)  # 货币
    sale_price = product.get("sale_price", None)  # 销售价格
    sale_price = float(sale_price) if sale_price is not None else sale_price
    msg.append(
        [
            {
                "tag": "text",
                "text": f"不含税价格: {sale_price} {currency}"
            }
        ]
    )
    vat = float(product.get("vat", None)) if product.get("vat", None) else product.get("vat", None)  # 增值税
    msg.append(
        [
            {
                "tag": "text",
                "text": f"vat: {vat * 100}%"
            }
        ]
    )
    msg.append(
        [
            {
                "tag": "text",
                "text": f"含税价格: {round(sale_price * (1 + vat))} {currency}"
            }
        ]
    )
    quantity = product.get("quantity", None)  # 数量
    msg.append(
        [
            {
                "tag": "text",
                "text": f"数量: {quantity}"
            }
        ]
    )

    msg.append(
        [
            {
                "tag": "text",
                "text": f"---------------------"
            }
        ]
    )
    return msg


@retry(stop_max_attempt_number=5, wait_random_min=1000, wait_random_max=2000)
def send_to_fei_shu(msg, url):
    if not url:
        return
    data = json.dumps({
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": "来单咯!",
                    "content": msg
                }
            }
        }
    })
    resp = requests.post(url=url,
                         data=data)
    time.sleep(1)


def save_data(orders, country, shop_id, campany_id, order_notice_type, order_notice_url, em_orders_monitor_log_obj):
    today = datetime.today()
    add = []
    if not orders["isError"]:
        modifiedBeforeLast = em_orders_monitor_log_obj.lastModified
        for order in orders["results"]:
            modifiedBeforeLast_ = order.get("modified", None)
            if not modifiedBeforeLast or modifiedBeforeLast_.replace(":","").replace(" ","").replace("-","")>modifiedBeforeLast.replace(":","").replace(" ","").replace("-",""):
                modifiedBeforeLast = modifiedBeforeLast_
            if order.get("payment_status", None) == 1 or order.get("status", None) in [1, 2, 3, 4]:
                # 加入任务队列
                if order.get("status", None) in [0,4,5]:
                    modified = str_to_datetime(order.get("modified", None))
                    add.append({
                        "campanyId": campany_id,
                        "shop": shop_id,
                        "country": country,
                        "orderId": order["id"],
                        "status": 0,
                        "modified": modified
                    })
                #

                if em_orders_model.objects(orderId=order["id"], country=country).count() == 0:
                    order["orderId"] = order.pop("id")
                    date_ = order["date"]
                    order["date"] = datetime.strptime(order["date"], '%Y-%m-%d %H:%M:%S')
                    order["totalPriceRmb"] = cal_order_total_pcost(order)
                    order["country"] = country
                    order["shop"] = shop_id
                    order["campanyId"] = campany_id
                    to_mongo(em_orders_model, [order], ["campanyId", "shop", "country", "orderId"])
                    msg = parse_order(order)
                    # if date_>today-timedelta(days=3):  # 只发送今日订单
                    if order_notice_type == "feishu":
                        send_to_fei_shu(msg, order_notice_url)
                else:
                    order["orderId"] = order.pop("id")
                    order["date"] = datetime.strptime(order["date"], '%Y-%m-%d %H:%M:%S')
                    order["totalPriceRmb"] = cal_order_total_pcost(order)
                    order["country"] = country
                    order["shop"] = shop_id
                    order["campanyId"] = campany_id
                    to_mongo(em_orders_model, [order], ["campanyId", "shop", "country", "orderId"])
            else:
                order["orderId"] = order.pop("id")
                order["date"] = datetime.strptime(order["date"], '%Y-%m-%d %H:%M:%S')
                order["totalPriceRmb"] = cal_order_total_pcost(order)
                order["country"] = country
                order["shop"] = shop_id
                order["campanyId"] = campany_id
                to_mongo(em_orders_model, [order], ["campanyId", "shop", "country", "orderId"])
                if order.get("status", None) == 0:
                    pass
                elif order.get("status", None) == 5:
                    pass
        if modifiedBeforeLast and em_orders_monitor_log_obj:
            em_orders_monitor_log_obj.lastModified = modifiedBeforeLast
            em_orders_monitor_log_obj.save()
    if add:
        to_mongo(order_modify_queue_model, add, ["campanyId", "shop", "country", "orderId", "modified"])

def task(country, shop_id, campany_id, shop_hash, order_notice_type, order_notice_url):
    logger.info(f"店铺->{shop_id} 站点->{country}")
    # 查询记录
    em_orders_monitor_log_obj = em_orders_monitor_log_model.objects(campanyId=campany_id, shopId=shop_id,
                                                                    country=country).first()
    if not em_orders_monitor_log_obj or not em_orders_monitor_log_obj.lastModified:
        logger.info(f"开始初始化")
        if not em_orders_monitor_log_obj:
            em_orders_monitor_log_model(campanyId=campany_id, shopId=shop_id, country=country, lastModified=None).save()
        # 初始化
        count_resp = OrderApi.count(shop_hash=shop_hash, country=country)
        pages = int(count_resp["results"]["noOfPages"])
        #
        for page in tqdm(range(1,pages+1)):
            em_orders_monitor_log_obj = em_orders_monitor_log_model.objects(campanyId=campany_id, shopId=shop_id,
                                                                            country=country).first()
            orders = OrderApi.read(shop_hash=shop_hash, current_page=page, items_per_page=100, country=country,modifiedAfter=None,
                               modifiedBefore=None)
            save_data(orders, country, shop_id, campany_id, order_notice_type, order_notice_url,
                      em_orders_monitor_log_obj)
    #
    else:
        modifiedAfter =date_add_1_s(em_orders_monitor_log_obj.lastModified)
        modifiedBefore = get_modified_before(em_orders_monitor_log_obj.lastModified)
        orders = OrderApi.read(shop_hash=shop_hash, current_page=1, items_per_page=100, country=country,
                               modifiedAfter=modifiedAfter,
                               modifiedBefore=modifiedBefore)
        save_data(orders, country, shop_id, campany_id, order_notice_type, order_notice_url, em_orders_monitor_log_obj)


def task_main(shop_id, campany_id, shop_hash, order_notice_type, order_notice_url):
    for country in ["ro", "bg", "hu"]:
        try:
            task(country, shop_id, campany_id, shop_hash, order_notice_type, order_notice_url)
        except Exception as e:
            logger.exception(e)
            pass


def main():
    pool = ThreadPoolExecutor(10)
    while True:
        print(2)
        shop_objs = shop_model.objects(em_login_info__hash__ne=None).only("shop_id", "campanyId", "em_login_info",
                                                                          "noticeUrls")
        for shop_obj in shop_objs:

            shop_id = shop_obj.shop_id
            print(shop_id)
            #if shop_id!="UF":continue
            campany_id = shop_obj.campanyId
            if not campany_model.objects(campanyId=campany_id, isSvip=True).first():
                print(1)
                continue
            shop_hash = shop_obj.em_login_info.get("hash", None)
            order_notice_info = shop_obj.noticeUrls.get("orderNotice", {})
            order_notice_type = order_notice_info.get("type", None)
            order_notice_url = order_notice_info.get("url", None)
            order_notice_open = order_notice_info.get("open", False)
            if not order_notice_open:
                continue
            if shop_hash:# and order_notice_type and order_notice_url:
                #task_main( shop_id, campany_id, shop_hash, order_notice_type, order_notice_url)
                pool.submit(task_main, shop_id, campany_id, shop_hash, order_notice_type, order_notice_url)
        time.sleep(60)
    pool.shutdown(wait=True)

def update_offer_cost():
    """
    修复价格
    """
    objs = em_orders_model.objects()
    for obj in objs:
        a = cal_order_total_pcost(obj.to_mongo().to_dict())
        if a!=obj.totalPriceRmb:
            print(a,obj.totalPriceRmb)
        obj.update(totalPriceRmb=a)




if __name__ == '__main__':
    # 代理 microsocks -1 -u coisin -P swlcyx2019
    campany_model = ModelManager.get_model("campany", "base")
    shop_model = ModelManager.get_model("shop", "base")
    # listing_model = ModelManager.get_model("listing", "base")
    em_orders_monitor_log_model = ModelManager.get_model("em_orders_monitor_log", "base")
    order_status = {0: "Canceled", 1: "New", 2: "In progress", 3: "Prepared", 4: "Finalized", 5: "Returned"}
    payment_status_dict = {0: "未支付", 1: "已支付"}
    em_orders_model = ModelManager.get_model("em_orders", "base")
    order_modify_queue_model = ModelManager.get_model("order_modify_queue", "base")
    main()
    # print(OrderApi.read(1, 10, country="hu", createdAfter="2024-09-23 21:10:05")["results"][-1])
    # update_offer_cost()