# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：em_api_server.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-04-12 21:48 
-------------------------------------
'''
import requests
from flask import Flask
from flask import request
import logging

from flask_cors import CORS

log = logging.getLogger('werkzeug')  # 去除日志打印
log.setLevel(logging.ERROR)

app = Flask(__name__)
CORS(app, supports_credentials=True)  # 允许跨域


@app.route('/api/post/', methods=["POST"])
def post():
    try:
        url = request.json.get("url", None)
        headers = request.json.get("headers", None)
        data = request.json.get("data", None)
        response = requests.request("POST", url, headers=headers, data=data, timeout=15)
        return response.json()
    except Exception as e:
        return {"error": str(e)}, 400


@app.route('/api/get/', methods=["POST"])
def get():
    try:
        url = request.json.get("url", None)
        headers = request.json.get("headers", None)
        response = requests.request("GET", url, headers=headers, timeout=15)
        return response.json()
    except Exception as e:
        return {"error": str(e)}, 400


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8887, threaded=True)
