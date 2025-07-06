# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：main_pro.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024-11-17 16:18 
-------------------------------------
'''
from utils.init_app import app
from apps import blue_print_group
# 注册蓝图
app.blueprint(blue_print_group)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9001, dev=True)
