# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：1688_api_server.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-02-05 14:19 
-------------------------------------
'''
import json
from loguru import logger
from flask import Flask
from flask import request
import logging

from flask_cors import CORS
from api_1688.api_1688_tool import Api1688

log = logging.getLogger('werkzeug')  # 去除日志打印
# log.setLevel(logging.ERROR)

app = Flask(__name__)
CORS(app, supports_credentials=True)  # 允许跨域


@app.route('/api1688/get_address/<campany_id>', methods=["GET"])
def get_address(campany_id):
    try:
        return {"code": 200, "data": Api1688.ADDRESS_INFO.get(campany_id,{})}
    except Exception as e:
        logger.exception(e)
        return {"error": str(e)}, 400


@app.route('/api1688/create_order/', methods=["POST"])
def create_order():
    try:
        address_id = request.json.get("address_id", None)
        skus_data = request.json.get("skus_data", None)
        tip_for_seller = request.json.get("tip_for_seller", None)
        token = request.json.get("token", None)
        resp = Api1688.create_order(address_id=address_id, skus_data=skus_data, tip_for_seller=tip_for_seller,
                                    token=token)
        return {"code": 200, "data": resp}
    except Exception as e:
        logger.exception(e)
        return {"error": str(e)}, 400


@app.route('/api1688/get_alipay_url/', methods=["POST"])
def get_alipay_url():
    try:
        order_id = request.json.get("order_id", None)
        token = request.json.get("token", None)
        resp = Api1688.get_alipay_url(order_id=order_id, token=token)
        return {"code": 200, "data": resp}
    except Exception as e:
        return {"error": str(e)}, 400


@app.route('/api1688/get_order_info/', methods=["POST"])
def get_order_info():
    try:
        order_id = request.json.get("order_id", None)
        token = request.json.get("token", None)
        resp = Api1688.get_order_info(order_id=order_id, token=token)
        return {"code": 200, "data": resp}
    except Exception as e:
        return {"error": str(e)}, 400


@app.route('/api1688/init_address/', methods=["POST"])
def init_address():
    shop_id = request.json.get("shop_id", None)
    token1688 = request.json.get("token1688", None)
    campany_id = request.json.get("campany_id", None)
    print(campany_id)

    Api1688.get_address(shop_id=shop_id, token=token1688,campany_id=campany_id)
    return {"code": 200, "data": {}}


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9092, threaded=True)
