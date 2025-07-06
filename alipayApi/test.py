# -*- coding: UTF-8 -*-
'''
@Project     ：em_buy_carts_monitor_backen 
@File        ：alipay_tool.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-03-07 23:27 
-------------------------------------
'''
from alipay import AliPay, DCAliPay, ISVAliPay
from alipay.utils import AliPayConfig

# 支付宝网页下载的证书不能直接被使用，需要加上头尾
# 你可以在此处找到例子： tests/certs/ali/ali_private_key.pem
app_private_key_string = open("config/privateKey.txt").read()
alipay_public_key_string = open("config/alipayPublicCert.txt").read()

alipay = AliPay(
    appid="2021005121696985",
    app_notify_url=None,  # 默认回调 url
    app_private_key_string=app_private_key_string,
    # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
    alipay_public_key_string=alipay_public_key_string,
    sign_type="RSA2",  # RSA 或者 RSA2
    debug=False,  # 默认 False
    verbose=False,  # 输出调试数据
    config=AliPayConfig(timeout=15)  # 可选，请求超时时间
)

# 支付参数
subject = "商品名称"
out_trade_no = "17415395201304371"  # 商户订单号，需保证唯一
# total_amount = 0.01  # 订单总金额
#
# # 发起支付请求
# order_string = alipay.api_alipay_trade_page_pay(
#     out_trade_no=out_trade_no,
#     total_amount=total_amount,
#     subject=subject,
#     qr_pay_mode="4",  # 扫码支付的方式。
#     # time_expire=""
#
# )
#
# # 生成支付链接
# pay_url = "https://openapi.alipay.com/gateway.do?" + order_string
# print(pay_url)
# 要退款的订单号
# 退款金额
refund_amount = 0.01
# 退款原因
refund_reason = "用户申请退款"

# 发起退款请求
result = alipay.api_alipay_trade_refund(
    out_trade_no=out_trade_no,
    refund_amount=refund_amount,
    refund_reason=refund_reason
)

if result.get("code") == "10000":
    print("退款申请成功")
else:
    print(f"退款申请失败，错误信息：{result.get('msg')}")

# 查询订单
# result = alipay.api_alipay_trade_query(out_trade_no=out_trade_no)
# if result.get("trade_status") == "TRADE_SUCCESS":
#     print("订单支付成功")
#
#     # 发起退款请求
#     refund_amount = 9.9
#     refund_reason = "用户申请退款"
#     refund_result = alipay.api_alipay_trade_refund(
#         out_trade_no=out_trade_no,
#         refund_amount=refund_amount,
#         refund_reason=refund_reason
#     )
#     if refund_result.get("code") == "10000":
#         print("退款申请成功")
#
#         # 查询退款状态
#         out_request_no = "your_out_request_no"
#         refund_query_result = alipay.api_alipay_trade_fastpay_refund_query(
#             out_trade_no=out_trade_no,
#             out_request_no=out_request_no
#         )
#         if refund_query_result.get("code") == "10000":
#             refund_status = refund_query_result.get("refund_status")
#             print(f"退款状态：{refund_status}")
#         else:
#             print(f"退款查询失败，错误信息：{refund_query_result.get('msg')}")
#     else:
#         print(f"退款申请失败，错误信息：{refund_result.get('msg')}")
# else:
#     print(f"订单状态：{result.get('trade_status')}")
