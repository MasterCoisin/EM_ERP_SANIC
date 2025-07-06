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
@Date        ：2025-05-16 12:01 
-------------------------------------
'''
import datetime

from motor.motor_asyncio import AsyncIOMotorCollection
from sanic import Sanic

from apps.listing.tool import get_ean_and_images_by_id, fbe_fee_cal_obj
from apps.msku_inventory_detail.tool import count_sold_by_batch
from apps.msku_inventory_index.tool import get_data_by_ean
from config.constant import COUNTRY_TO_CURRENCY, EXCHANGE, APP_NAME
from models.em_order import EmOrder
from utils.common import TO_RMB, price_deal

app = Sanic.get_app(APP_NAME)
MERGER_BEGIN = 17


async def parse_em_order_info(data):
    country = data["country"]
    currency = COUNTRY_TO_CURRENCY[country]
    # 时间处理
    if data.get("date"):
        data["date"] = data["date"].timestamp()
    # 订单金额
    data[
        "totalPriceWithoutVat"] = f'{sum([float(i["sale_price"]) * i["quantity"] for i in data.get("products", [])])} {currency}'
    data[
        "totalPriceWithoutVatRmb"] = f'{round(sum([float(i["sale_price"]) * i["quantity"] * EXCHANGE[country] for i in data.get("products", [])]), 2)} RMB'
    data[
        "totalPriceWithVat"] = f'{round(sum([float(i["sale_price"]) * i["quantity"] * (1 + float(i["vat"])) for i in data.get("products", [])]), 2)} {currency}'
    data[
        "totalPriceWithVatRmb"] = f'{round(sum([float(i["sale_price"]) * i["quantity"] * (1 + float(i["vat"])) * EXCHANGE[country] for i in data.get("products", [])]), 2)} RMB'
    # genius费用
    geniusDeliveryFee = 0
    if data.get("flags", []):
        for flag in data.get("flags", []):
            if flag.get("flag", None) == "genius_delivery_fee":
                geniusDeliveryFee = float(flag.get("value"))
                break
    data["geniusDeliveryFee"] = f"{geniusDeliveryFee} {currency}"

    return data


async def get_today_orders(campany_id, shop):
    collection: AsyncIOMotorCollection = app.ctx.mongo[EmOrder.collection_name]
    today = datetime.datetime.today()-datetime.timedelta(hours=5)
    result = collection.find({"campanyId": campany_id, "shop": shop,
                              "date": {
                                  "$gte": datetime.datetime(year=today.year, month=today.month, day=today.day),
                                  "$lte": datetime.datetime(year=today.year, month=today.month, day=today.day,hour=23,minute=59,second=59)}},
                             {"_id": 0}).sort("date", direction=-1)
    orders = []
    mergeCells = []
    ean_data = {}
    orderProfitData = {}
    try:
        eanDatas = {
            "ro": {},
            "bg": {},
            "hu": {}
        }
        product_id_by_country = {
            "ro": [],
            "bg": [],
            "hu": []
        }
        for document in await result.to_list():
            country = document.get("country", None)
            orderId = document.get("orderId", None)
            customerName = document.get("customer", {}).get("name", None)
            customerId = document.get("customer", {}).get("id", None)
            delivery_mode = document.get("delivery_mode", None)
            status = document.get("status", 0)
            costStructure = document.get("costStructure", {})

            # genius费用
            geniusDeliveryFee = 0
            if document.get("flags", []):
                for flag in document.get("flags", []):
                    if flag.get("flag", None) == "genius_delivery_fee":
                        geniusDeliveryFee = float(flag.get("value"))
                        break
            # 订单金额
            order_amount_total_without_vat = 0
            order_amount_total_with_vat = 0
            order_amount_total_without_vat_by_seller = 0
            order_amount_total_with_vat_by_seller = 0
            order_amount_total_without_vat_by_emag = 0
            order_amount_total_with_vat_by_emag = 0
            # 总优惠券
            voucher_amount_by_seller_total = 0  # 店铺优惠券不含税总额
            voucher_vat_amount_by_seller_total = 0  # 店铺优惠券税费
            voucher_amount_by_emag_total = 0  # 平台优惠券不含税总额
            voucher_vat_amount_by_emag_total = 0  # 平台优惠券税费
            # 利润计算
            products = document.get("products", [])
            orders_ = []
            currency = None
            for idx, product_info in enumerate(products):
                part_number_key = product_info.get("part_number_key", None)
                product_id = int(product_info.get("product_id", None))
                currency = product_info.get("currency", None)
                product_voucher_split = product_info.get("product_voucher_split", [])
                quantity = product_info.get("quantity", None)
                sale_price = float(product_info.get("sale_price", None))
                vat = float(product_info.get("vat", None))
                sale_price_total_without_vat = round(sale_price * quantity, 4)
                sale_price_total_with_vat = round(sale_price * quantity * (1 + vat), 4)

                # 优惠券
                voucher_amount_by_seller = 0  # 店铺优惠券不含税总额
                voucher_vat_amount_by_seller = 0  # 店铺优惠券税费
                voucher_amount_by_emag = 0  # 平台优惠券不含税总额
                voucher_vat_amount_by_emag = 0  # 平台优惠券税费
                for voucher in product_voucher_split:
                    if voucher.get("offered_by", None) == "seller":
                        voucher_amount_by_seller = -voucher.get("value", 0)
                        voucher_vat_amount_by_seller = -voucher.get("vat_value", 0)
                    else:
                        voucher_amount_by_emag = -voucher.get("value", 0)
                        voucher_vat_amount_by_emag = -voucher.get("vat_value", 0)

                order_amount_total_without_vat += sale_price * quantity
                order_amount_total_with_vat += sale_price * quantity * (1 + vat)

                order_amount_total_without_vat_by_seller += (sale_price_total_without_vat - voucher_amount_by_seller)
                order_amount_total_with_vat_by_seller += (
                        sale_price_total_with_vat - voucher_amount_by_seller - voucher_vat_amount_by_seller)

                order_amount_total_without_vat_by_emag += (
                        sale_price_total_without_vat - voucher_amount_by_seller - voucher_amount_by_emag)
                order_amount_total_with_vat_by_emag += (
                        sale_price_total_with_vat - voucher_amount_by_seller - voucher_vat_amount_by_seller - voucher_amount_by_emag - voucher_vat_amount_by_emag)
                #
                voucher_amount_by_seller_total += voucher_amount_by_seller  # 店铺优惠券不含税总额
                voucher_vat_amount_by_seller_total += voucher_vat_amount_by_seller  # 店铺优惠券税费
                voucher_amount_by_emag_total += voucher_amount_by_emag  # 平台优惠券不含税总额
                voucher_vat_amount_by_emag_total += voucher_vat_amount_by_emag  # 平台优惠券税费

                if status == 0:
                    order_amount_total_without_vat_by_seller = 0
                    order_amount_total_with_vat_by_seller = 0
                    order_amount_total_without_vat_by_emag = 0
                    order_amount_total_with_vat_by_emag = 0
                #
                orders_.append(
                    {
                    "orderId": orderId,
                    "country": country,
                    "customerName": customerName,
                    "customerId": customerId,
                    "delivery_mode": delivery_mode,
                    "status": status,
                    "geniusDeliveryFee": geniusDeliveryFee,

                    "order_amount_total_without_vat": order_amount_total_without_vat,
                    "order_amount_total_with_vat": order_amount_total_with_vat,

                    "order_amount_total_without_vat_by_seller": round(order_amount_total_without_vat_by_seller, 2),
                    "order_amount_total_with_vat_by_seller": round(order_amount_total_with_vat_by_seller, 2),
                    "order_amount_total_without_vat_by_seller_rmb": round(
                        order_amount_total_without_vat_by_seller * TO_RMB.get(currency), 2),
                    "order_amount_total_with_vat_by_seller_rmb": round(
                        order_amount_total_with_vat_by_seller * TO_RMB.get(currency), 2),

                    "order_amount_total_without_vat_by_emag": round(order_amount_total_without_vat_by_emag, 2),
                    "order_amount_total_with_vat_by_emag": round(order_amount_total_with_vat_by_emag, 2),
                    "order_amount_total_without_vat_by_emag_rmb": round(
                        order_amount_total_without_vat_by_emag * TO_RMB.get(currency), 2),
                    "order_amount_total_with_vat_by_emag_rmb": round(
                        order_amount_total_with_vat_by_emag * TO_RMB.get(currency), 2),

                    "part_number_key": part_number_key,
                    "product_id": product_id,
                    "currency": currency,
                    "product_voucher_split": product_voucher_split,
                    "quantity": quantity,
                    "sale_price": sale_price,

                    "sale_price_without_vat": round(sale_price * quantity, 2),
                    "sale_price_with_vat": round(sale_price * quantity * (1 + vat), 2),
                    "sale_price_without_vat_rmb": round(sale_price * quantity * TO_RMB.get(currency), 2),
                    "sale_price_with_vat_rmb": round(sale_price * quantity * (1 + vat) * TO_RMB.get(currency), 2),
                    # 产品含优惠券价格
                    "sale_price_without_vat_by_seller": round(sale_price * quantity - voucher_amount_by_seller, 2),
                    "sale_price_with_vat_by_seller": round(
                        (sale_price * quantity * (1 + vat) - voucher_amount_by_seller - voucher_vat_amount_by_seller), 2),
                    "sale_price_without_vat_by_seller_rmb": round(
                        (sale_price * quantity - voucher_amount_by_seller) * TO_RMB.get(currency), 2),
                    "sale_price_with_vat_by_seller_rmb": round(
                        (sale_price * quantity * (
                                1 + vat) - voucher_amount_by_seller - voucher_vat_amount_by_seller) * TO_RMB.get(
                            currency), 2),

                    # 产品含优惠券价格
                    "sale_price_without_vat_by_emag": round(
                        sale_price * quantity - voucher_amount_by_seller - voucher_amount_by_emag,
                        2),
                    "sale_price_with_vat_by_emag": round(
                        (
                                sale_price * quantity * (
                                1 + vat) - voucher_amount_by_seller - voucher_vat_amount_by_seller - voucher_amount_by_emag - voucher_vat_amount_by_emag),
                        2),
                    "sale_price_without_vat_by_emag_rmb": round(
                        (sale_price * quantity - voucher_amount_by_seller - voucher_amount_by_emag) * TO_RMB.get(currency),
                        2),
                    "sale_price_with_vat_by_emag_rmb": round(
                        (
                                sale_price * quantity * (
                                1 + vat) - voucher_amount_by_seller - voucher_vat_amount_by_seller - voucher_amount_by_emag - voucher_vat_amount_by_emag) * TO_RMB.get(
                            currency), 2),
                    #
                    "vat": vat,

                    "sale_price_single_without_vat": round(sale_price, 2),
                    "sale_price_single_with_vat": round(sale_price * (1 + vat), 2),
                    "sale_price_single_without_vat_rmb": round(sale_price * TO_RMB.get(currency), 2),
                    "sale_price_single_with_vat_rmb": round(sale_price * (1 + vat) * TO_RMB.get(currency), 2),

                    "voucher_amount_by_seller_without_vat": -round(voucher_amount_by_seller, 2),
                    "voucher_amount_by_seller_with_vat": -round(voucher_amount_by_seller + voucher_vat_amount_by_seller,
                                                                2),
                    "voucher_amount_by_seller_with_vat_rate": None if (
                                                                              sale_price * quantity) == 0 else f"{round(100 * voucher_amount_by_seller / (sale_price * quantity), 1)} %",
                    "voucher_amount_by_seller_without_vat_rmb": -round(voucher_amount_by_seller * TO_RMB.get(currency), 2),
                    "voucher_amount_by_seller_with_vat_rmb": -round(
                        (voucher_amount_by_seller + voucher_vat_amount_by_seller) * TO_RMB.get(currency),
                        2),

                    "voucher_amount_by_emag_without_vat": -round(voucher_amount_by_emag, 2),
                    "voucher_amount_by_emag_with_vat": -round(voucher_amount_by_emag + voucher_vat_amount_by_emag,
                                                              2),
                    "voucher_amount_by_emag_with_vat_rate": None if (
                                                                            sale_price * quantity) == 0 else f"{round(100 * voucher_amount_by_emag / (sale_price * quantity), 1)} %",

                    "voucher_amount_by_emag_without_vat_rmb": -round(voucher_amount_by_emag * TO_RMB.get(currency), 2),
                    "voucher_amount_by_emag_with_vat_rmb": -round(
                        (voucher_amount_by_emag + voucher_vat_amount_by_emag) * TO_RMB.get(currency),
                        2),

                    "voucher_amount_by_seller_without_vat_total": -round(voucher_amount_by_seller_total, 2),
                    "voucher_amount_by_seller_with_vat_total": -round(
                        voucher_amount_by_seller_total + voucher_vat_amount_by_seller_total,
                        2),
                    "voucher_amount_by_seller_without_vat_rmb_total": -round(
                        voucher_amount_by_seller_total * TO_RMB.get(currency), 2),
                    "voucher_amount_by_seller_with_vat_rmb_total": -round(
                        (voucher_amount_by_seller_total + voucher_vat_amount_by_seller_total) * TO_RMB.get(currency),
                        2),

                    "voucher_amount_by_emag_without_vat_total": -round(voucher_amount_by_emag_total, 2),
                    "voucher_amount_by_emag_with_vat_total": -round(
                        voucher_amount_by_emag_total + voucher_vat_amount_by_emag_total,
                        2),
                    "voucher_amount_by_emag_without_vat_rmb_total": -round(
                        voucher_amount_by_emag_total * TO_RMB.get(currency),
                        2),
                    "voucher_amount_by_emag_with_vat_rmb_total": -round(
                        (voucher_amount_by_emag_total + voucher_vat_amount_by_emag_total) * TO_RMB.get(currency),
                        2),

                    "border_buttom": False,
                    "product_index": idx,
                    "costStructure": costStructure.get(str(product_id), {})
                })
                product_id_by_country[country].append(product_id)
            for idx in range(len(orders_)):
                orders_[idx]["order_amount_total_without_vat"] = order_amount_total_without_vat
                orders_[idx]["order_amount_total_with_vat"] = order_amount_total_with_vat
                orders_[idx]["order_amount_total_without_vat_by_seller"] = round(order_amount_total_without_vat_by_seller, 2)
                orders_[idx]["order_amount_total_with_vat_by_seller"] = round(order_amount_total_with_vat_by_seller, 2)
                orders_[idx]["order_amount_total_without_vat_by_seller_rmb"] = round(
                            order_amount_total_without_vat_by_seller * TO_RMB.get(currency), 2)
                orders_[idx]["order_amount_total_with_vat_by_seller_rmb"] = round(
                            order_amount_total_with_vat_by_seller * TO_RMB.get(currency), 2)
                orders_[idx]["order_amount_total_without_vat_by_emag"] = round(order_amount_total_without_vat_by_emag, 2)
                orders_[idx]["order_amount_total_with_vat_by_emag"] = round(order_amount_total_with_vat_by_emag, 2)
                orders_[idx]["order_amount_total_without_vat_by_emag_rmb"] = round(
                            order_amount_total_without_vat_by_emag * TO_RMB.get(currency), 2)
                orders_[idx]["order_amount_total_with_vat_by_emag_rmb"] = round(
                            order_amount_total_with_vat_by_emag * TO_RMB.get(currency), 2)

            orders_[-1]["border_buttom"] = "True"
            n = len(orders_)
            if n > 1:
                mergeCells.append({"row": len(orders), "col": 0, "rowspan": n, "colspan": 1})
                mergeCells.append({"row": len(orders), "col": 1, "rowspan": n, "colspan": 1})
                mergeCells.append({"row": len(orders), "col": 2, "rowspan": n, "colspan": 1})
                mergeCells.append({"row": len(orders), "col": 3, "rowspan": n, "colspan": 1})
                mergeCells.append({"row": len(orders), "col": MERGER_BEGIN + 0, "rowspan": n, "colspan": 1})
                mergeCells.append({"row": len(orders), "col": MERGER_BEGIN + 1, "rowspan": n, "colspan": 1})
                mergeCells.append({"row": len(orders), "col": MERGER_BEGIN + 2, "rowspan": n, "colspan": 1})
            orders += orders_
        # 获取产品基本数据
        for country in ["ro", "bg", "hu"]:
            if product_id_by_country[country]:
                eanDatas[country] = await get_ean_and_images_by_id(campany_id, shop, product_id_by_country[country],
                                                                   country)
        ean_data_ = {}
        for item in orders:
            info_ = eanDatas.get(item["country"], {}).get(item["product_id"], {})
            item["images"] = info_.get("images", [])
            item["ean"] = info_.get("ean", None)
            item["stock"] = info_.get("stock", None)
            item["commission"] = info_.get("commission", None)
            if info_.get("ean", None):
                fbeFee = await fbe_fee_cal_obj.cal_fbe_fee(
                    info_["lengthWidthHeightWeight"]["G"] * 1000 if info_["lengthWidthHeightWeight"]["G"] else
                    info_["lengthWidthHeightWeight"]["G"],
                    info_["lengthWidthHeightWeight"]["L"] if info_["lengthWidthHeightWeight"]["L"] else
                    info_["lengthWidthHeightWeight"]["L"],
                    info_["lengthWidthHeightWeight"]["W"] if info_["lengthWidthHeightWeight"]["W"] else
                    info_["lengthWidthHeightWeight"]["W"],
                    info_["lengthWidthHeightWeight"]["H"] if info_["lengthWidthHeightWeight"]["H"] else
                    info_["lengthWidthHeightWeight"]["H"])
                ean_data_[info_.get("ean", None)] = {"stock": info_.get("stock", None), "fbeFee": fbeFee}

        ean_stock_data = await get_data_by_ean(list(ean_data_.keys()))
        # 销量
        count_sold_by_batch_data = await count_sold_by_batch(company_id=campany_id, eans=list(ean_data_.keys()))
        ean_data = {i["ean"]: {
            "stock": ean_data_[i['ean']]['stock'],
            "fbeFee": ean_data_[i['ean']]['fbeFee'].get("orderFeeRmb", None),
            "mskuAvgFee": price_deal(i.get("mskuAvgFee", None)),
            "mskuFinallInboundDate": i.get("mskuFinallInboundDate", None),
            "mskuFirstInboundDate": i.get("mskuFirstInboundDate", None),
            "mskuHasDestroyed": i.get("mskuHasDestroyed", None),
            "mskuHasLosed": i.get("mskuHasLosed", None),
            "mskuHasPurchased": i.get("mskuHasPurchased", None),
            "mskuHasPurchasedRate": None if (
                    i.get("mskuHasPurchased", None) is None or i.get("mskuTotalSent", None) is None or i.get(
                "mskuTotalSent",
                None) == 0) else f"({round(100 * i.get('mskuHasPurchased', None) / i.get('mskuTotalSent', None), 1)}%)",
            "mskuSendTimes": i.get("mskuSendTimes", None),
            "mskuTotalSent": i.get("mskuTotalSent", None),
            "mskuLeft": i.get("mskuLeft", None),
            "mskuInTrans": i.get("mskuInTrans", None),
            "mskuAvgBuyAndHeadFee": price_deal(i.get("mskuAvgBuyAndHeadFee", None)),
            "mskuAvgHeadFee": price_deal(i.get("mskuAvgHeadFee", None)),
            "soldCount": count_sold_by_batch_data.get(i.get("ean", None),
                                                      {'week': 0, 'month': 0, 'season': 0, 'year': 0}),
            "predSoldMonth": round(ean_data_[i['ean']]['stock'] / count_sold_by_batch_data.get(i.get("ean", None),
                                                                                               {'week': 0, 'month': 0,
                                                                                                'season': 0,
                                                                                                'year': 0}).get('month', 0),
                                   1) if count_sold_by_batch_data.get(i.get("ean", None),
                                                                      {'week': 0, 'month': 0, 'season': 0, 'year': 0}).get(
                'month', 0) else None
        } for i in await ean_stock_data}
        # 利润计算
        order_total_profit_cal_base_data = {}  # 计算订单的利润数据
        for item in orders:
            orderId = item["orderId"]
            currency = item["currency"]
            if orderId not in order_total_profit_cal_base_data:
                order_total_profit_cal_base_data[orderId] = {
                    "profitRmb": 0,
                    "sale_price_with_vat_by_seller_rmb": 0
                }

            costStructure = item["costStructure"]
            quantity = item["quantity"]
            if not costStructure:
                costStructure = {
                    "mskuFee": ean_data.get(item["ean"], {}).get("mskuAvgFee", None)*quantity,
                    "mskuHeadFee": ean_data.get(item["ean"], {}).get("mskuAvgHeadFee", None)*quantity
                }
                item["costStructure"] = costStructure
            commission = item["commission"]
            sale_price = item["sale_price"]  # 不含税单价
            status = item["status"]
            geniusDeliveryFee = item["geniusDeliveryFee"]
            fbeFee = ean_data.get(item["ean"], {}).get("fbeFee", None)
            order_amount_total_without_vat = item["order_amount_total_without_vat"]  # 订单总含税金额（未扣除优惠券）
            order_amount_total_with_vat = item["order_amount_total_without_vat"]  # 订单总不含税金额（未扣除优惠券）
            voucher_amount_by_seller_without_vat = -item["voucher_amount_by_seller_without_vat"]  # 活动优惠券
            sale_price_with_vat_by_seller_rmb = item["sale_price_with_vat_by_seller_rmb"]
            if sale_price is None or commission is None or quantity is None or costStructure[
                "mskuFee"] is None or costStructure["mskuHeadFee"] is None or order_total_profit_cal_base_data[
                orderId] is None or fbeFee is None:
                # 无法计算利润
                order_total_profit_cal_base_data[orderId] = None
                profitRmb = None
                profitRate = None
            else:
                order_total_profit_cal_base_data[orderId]["sale_price_with_vat_by_seller_rmb"] += sale_price_with_vat_by_seller_rmb
                if status==4:
                    # 利润计算 不含税总金额*(1-佣金)-不含税活动优惠券-genius分配 - FBE -头程 - 产品进货价
                    profitRmb = (sale_price * quantity * (
                                1 - commission / 100.0) - voucher_amount_by_seller_without_vat - geniusDeliveryFee * sale_price* quantity / order_amount_total_without_vat) * TO_RMB.get(
                        currency) - fbeFee* quantity - costStructure["mskuFee"] - costStructure["mskuHeadFee"]
                    order_total_profit_cal_base_data[orderId]["profitRmb"] += profitRmb
                    profitRate = f"{round(100 * profitRmb / sale_price_with_vat_by_seller_rmb, 2)} %"
                elif status == 5:
                    profitRmb = -fbeFee* quantity
                    order_total_profit_cal_base_data[orderId]["profitRmb"] += profitRmb
                    profitRate = None
                else:
                    order_total_profit_cal_base_data[orderId] = None
                    profitRmb = None
                    profitRate = None
            item["profitRmb"] = round(profitRmb,2) if profitRmb else profitRmb
            item["profitRate"] = profitRate
        orderProfitData = {k: {"profitRmb": round(v["profitRmb"],2) if v["profitRmb"] else v["profitRmb"],
                                                "profitRate": f"{round(100 * v['profitRmb'] / v['sale_price_with_vat_by_seller_rmb'], 2)} %" if v['sale_price_with_vat_by_seller_rmb'] else None} if v is not None else {
            "profitRmb": None, "profitRate": None} for k, v in order_total_profit_cal_base_data.items()}
    except :
        pass
    return orders, mergeCells, ean_data,orderProfitData
