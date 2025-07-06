# -*- coding: UTF-8 -*-
'''
@Project     ：em_buy_carts_monitor_backen 
@File        ：alipayTook.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-03-08 14:57 
-------------------------------------
'''
from alipay import AliPay
from alipay.utils import AliPayConfig

from config.constant import APPID, APP_PRIVATE_KEY_PATH, ALIPAY_PUBLIC_KEY_PATH


class aliPayTool():
    app_private_key_string = open(APP_PRIVATE_KEY_PATH).read()
    alipay_public_key_string = open(ALIPAY_PUBLIC_KEY_PATH).read()
    alipay = AliPay(
        appid=APPID,
        app_notify_url=None,  # 默认回调 url
        app_private_key_string=app_private_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=False,  # 默认 False
        verbose=False,  # 输出调试数据
        config=AliPayConfig(timeout=15)  # 可选，请求超时时间
    )

    @classmethod
    def api_alipay_trade_page_pay(cls, subject, out_trade_no, total_amount, qr_pay_mode="4", **kwargs):
        """
        发起支付请求
        :param subject: 商品名称
        :param out_trade_no: 商户订单号，需保证唯一
        :param total_amount:订单总金额
        :param qr_pay_mode:扫码支付的方式
        :param kwargs:
        :return:
        """
        order_string = cls.alipay.api_alipay_trade_page_pay(
            out_trade_no=out_trade_no,
            total_amount=total_amount,
            subject=subject,
            qr_pay_mode=qr_pay_mode,
            notify_url="https://www.fzwala.com/api/alipayPro/messageReciver",

            **kwargs
        )
        # 生成支付链接
        pay_url = "https://openapi.alipay.com/gateway.do?" + order_string
        return pay_url

    @classmethod
    def api_alipay_trade_refund(cls, out_trade_no, refund_amount, refund_reason):
        """
        发起退款请求
        :param out_trade_no:要退款的订单号
        :param refund_amount:退款金额
        :param refund_reason:退款原因
        :return:
        """
        result = cls.alipay.api_alipay_trade_refund(
            out_trade_no=out_trade_no,
            refund_amount=refund_amount,
            refund_reason=refund_reason
        )

        if result.get("code") == "10000":
            return True, "退款申请成功"
        else:
            return False, result.get('msg')

    @classmethod
    def api_alipay_trade_query(cls,out_trade_no):
        """
        查询订单
        :param out_trade_no: 查询的订单号
        :return:
        """
        result = cls.alipay.api_alipay_trade_query(out_trade_no=out_trade_no)
        if result.get("trade_status") == "TRADE_SUCCESS":
            print("订单支付成功")
        else:
            print(f"订单状态：{result.get('trade_status')}")
        return result

    @classmethod
    def api_alipay_trade_fastpay_refund_query(cls,out_trade_no,out_request_no):
        """

        :param out_trade_no: 查询的订单号
        :param out_request_no: 查询的退款号号
        :return:
        """
        refund_query_result = cls.alipay.api_alipay_trade_fastpay_refund_query(
            out_trade_no=out_trade_no,
            out_request_no=out_request_no
        )
        if refund_query_result.get("code") == "10000":
            refund_status = refund_query_result.get("refund_status")
            print(f"退款状态：{refund_status}")
        else:
            print(f"退款查询失败，错误信息：{refund_query_result.get('msg')}")
