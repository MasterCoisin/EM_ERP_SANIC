# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BACKEN 
@File        ：common.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024/4/18 13:37 
-------------------------------------
'''
import base64
import re
import itertools
import time
import datetime
from config.constant import ALPHABET, NUMBER, RON_TO_RMB, BGN_TO_RMB, HUF_TO_RMB
from pymongo import UpdateOne
from loguru import logger
from uuid import uuid1

TO_RMB = {"RON": RON_TO_RMB, "HUF": HUF_TO_RMB, "BGN": BGN_TO_RMB}


def get_1688_product_id(url):
    try:
        return re.findall(f"offer/(.*?)\.html", url)[0]
    except:
        return None


def get_z_h():
    res = itertools.product(ALPHABET.copy(), ALPHABET.copy(), repeat=1)
    # 结果转化为列表
    result = list(res)
    return ["".join(list(i)) for i in res]


def transfer_date(target_time, return_str=True):
    """
    UTC世界标准时间（包含T和Z） 转 北京时间
    :param target_time:
    :return:
    """
    _date = datetime.datetime.strptime(target_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    local_time = _date + datetime.timedelta(hours=8)
    if return_str:
        end_time = local_time.strftime("%Y-%m-%d")
        return end_time
    else:
        return local_time.timestamp()


def get_regex(keyword):
    regex = re.compile(f".*?{keyword}.*?", re.IGNORECASE)  # 创建正则表达式
    return regex


def to_mongo(m, datas, filters):
    try:
        bulk_operations = [
            UpdateOne(
                {i: data[i] for i in filters},  # 查询条件
                {'$set': data},  # 更新的字段
                upsert=True  # 设置为True表示如果没有匹配到文档则插入新文档
            ) for data in datas
        ]
        # 执行批量操作
        m._get_collection().bulk_write(bulk_operations, ordered=False)
    except Exception as e:
        logger.exception(e)


def get_purchase_order_id():
    "创建采购单单号"
    s = "PO"
    t = datetime.datetime.today()
    return f"{s}{t.year - 2000}{t.month:0>2}{t.day:0>2}{t.hour:0>2}{t.minute:0>2}{t.second:0>2}"


def get_shipment_order_id():
    s = "SO"
    t = datetime.datetime.today()
    return f"{s}{t.year - 2000}{t.month:0>2}{t.day:0>2}{t.hour:0>2}{t.minute:0>2}{t.second:0>2}"


def get_packing_order_id():
    s = "PACK"
    t = datetime.datetime.today()
    return f"{s}{t.year - 2000}{t.month:0>2}{t.day:0>2}{t.hour:0>2}{t.minute:0>2}{t.second:0>2}"


def parse_str_to_float(s, devided=10):
    if s is None or s == "":
        return None
    else:
        return float(s) / devided


def parse_str_to_int(s):
    if s is None or s == "":
        return None
    else:
        return int(float(s))


def time_number_to_time_int(t):
    timeArray = time.localtime(t)
    return int(time.strftime("%Y%m%d", timeArray))


def get_today_time_int():
    return int(time.strftime("%Y%m%d", time.localtime(time.time())))


def get_html_image_detail(html):
    img_count, has_upload_image_count = 0, 0
    if not html:
        return img_count, has_upload_image_count
    html = html.replace("\r\n", " ")
    imgs = re.findall(r'https?://(.*?)\.(jpg|jpeg|png|gif)', html)
    img_count = len(imgs)
    for i in imgs:
        if "marketplace-static.emag.ro" in i[0]:
            has_upload_image_count += 1
    return img_count, has_upload_image_count


def cal_order_total_pcost(order):
    """
    计算订单总价
    :return:
    """
    total_price = 0
    for product in order.get("products", []):
        sale_price = product.get("sale_price", None)
        vat = product.get("vat", None)
        quantity = product.get("quantity", None)
        currency = product.get("currency", None)
        product_voucher_split = product.get("product_voucher_split",[])
        print(product_voucher_split)
        if sale_price and vat and quantity and quantity:
            total_price += float(sale_price) * (1 + float(vat)) * quantity * TO_RMB.get(currency)
            for voucher in product_voucher_split:
                if voucher.get("offered_by",None)=="seller":
                    total_price+=(voucher.get("value",0)+voucher.get("vat_value",0))* TO_RMB.get(currency)
    return total_price


def msku_to_sku_info(msku):
    sku_str = msku.split("-")[3:]
    return {i[:4]: int(i[4:]) for i in sku_str}


def get_uuid():
    return str(uuid1())


def to_float(s):
    if s is None or s == "":
        return None
    else:
        return float(s)


def args_valid(args: list):
    for arg in args:
        if arg is None:
            return False
    return True


def get_hash(s):
    return base64.b64encode(s.encode()).decode()


def price_deal(price,s=4):
    if not price:
        return price
    return round(price, s)


def datatime_to_timesmap(result):
    for k in ["createTime", "updateTime"]:
        if k in result:
            result[k] = result[k].timestamp()
    return result


def get_store_days(day=20240404):
    # 获取库存天数
    # 将日期字符串转换为datetime对象
    date1 = datetime.datetime.strptime(str(day), '%Y%m%d')
    # 计算天数差的绝对值
    delta = abs(datetime.datetime.today() - date1)
    return delta.days


def int_day_dec_days(days=7):
    # 日期加法
    date1 = datetime.datetime.today()
    date = date1 - datetime.timedelta(days=days)
    return int(date.strftime('%Y%m%d'))


def generate_year_weeks(start_year=None, start_week=None):
    # 获取今天的日期
    today = datetime.date.today()
    # 获取今天对应的年、周和星期几（ISO标准）
    year, week_num, day_of_week = today.isocalendar()
    if not start_year:
        return [[year, week_num - 1]], [[datetime.date.fromisocalendar(year, week_num, 1).strftime("%Y-%m-%d"),
                                         datetime.date.fromisocalendar(year, week_num, 7).strftime("%Y-%m-%d")]]
    # 结果列表
    year_weeks = []
    year_weeks_date_range = []

    # 计算开始日期：2024年的第28周的第一天
    start_date = datetime.date.fromisocalendar(start_year, start_week, 1)

    # 当前日期从开始日期开始
    current_date = start_date

    # 循环直到当前日期超过今天
    while current_date <= today:
        # 获取当前日期的年和周
        year, week, _ = current_date.isocalendar()
        year_weeks.append([year, week - 1])
        year_weeks_date_range.append(
            [current_date.strftime("%Y-%m-%d"), (current_date + datetime.timedelta(days=6)).strftime("%Y-%m-%d")])
        # 移动到下一周的第一天
        current_date += datetime.timedelta(days=7)

    return year_weeks, year_weeks_date_range


def get_day_range(start_date="2024-07-13"):
    # 获取今天的日期
    today = datetime.datetime.today()
    if not start_date:
        return [today.strftime("%Y-%m-%d")]
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    # 当前日期从开始日期开始
    current_date = start_date
    days = []
    # 循环直到当前日期超过今天
    while current_date <= today:
        days.append(current_date.strftime("%Y-%m-%d"))
        current_date += datetime.timedelta(days=1)
    return days


def get_month_range(start_date="2024-07"):
    # 获取今天的日期
    today = datetime.datetime.today()
    if not start_date:
        return [today.strftime("%Y-%m")]
    start_date = datetime.datetime.strptime(start_date, "%Y-%m")
    # 当前日期从开始日期开始
    current_date = start_date
    months = []
    # 循环直到当前日期超过今天
    while current_date <= today:
        if current_date.strftime("%Y-%m") not in months:
            months.append(current_date.strftime("%Y-%m"))
        current_date += datetime.timedelta(days=1)
    return months

def get_year_range(start_date="2024"):
    # 获取今天的日期
    today = datetime.datetime.today()
    if not start_date:
        return [today.strftime("%Y")]
    return [str(i) for i in range(int(start_date),today.year+1)]

