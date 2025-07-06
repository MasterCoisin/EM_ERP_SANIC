# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BACKEN 
@File        ：cal_fbe_fee.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024-08-25 11:19 
-------------------------------------
'''
from apps.config_data.tool import get_config_data_by_field_name
from config.constant import RON_TO_RMB


class CalFbeFee():
    def __init__(self):
        self.fbe_cal_config = None

    async def cal_fbe_fee(self, weight, length, width, height):
        """
        计算FBE费用
        :param weight: 重量(g)
        :param height: 高(mm)
        :param width: 宽(mm)
        :param length: 长(mm)
        :return:
        """
        if not self.fbe_cal_config:
            self.fbe_cal_config = await get_config_data_by_field_name(field_name="fbe_cal_config")
        if not weight or not height or not width or not length:
            return {'orderFeeRon': None, 'orderFeeRmb': None, 'removalFeeRon': None, 'disposalFeeRon': None}
        weight, height, width, length = float(weight), float(height), float(width), float(length)
        l_s = sorted([height, width, length])
        girth = 2 * (l_s[0] + l_s[1]) + l_s[2]

        base_girth, base_weight = None, None
        for g in self.fbe_cal_config["Girth"]:
            if g >= girth:
                base_girth = g
            else:
                break
        for w in self.fbe_cal_config["Weight"]:
            if w >= weight:
                base_weight = w
            else:
                break
        fee: dict = dict(self.fbe_cal_config["fee_standar"][str(int(base_girth))][str(int(base_weight))])
        fee["order_fee_rmb"] = round(float(fee["order_fee_ron"]) * RON_TO_RMB, 2)
        return {'orderFeeRon': fee.get("order_fee_ron", None), 'orderFeeRmb': fee.get("order_fee_rmb", None),
                'removalFeeRon': fee.get("removal_fee_ron", None), 'disposalFeeRon': fee.get("disposal_fee_ron", None)}

# print(CalFbeFee().cal_fbe_fee(128, 140, 100, 28))
