# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：init_app.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024-11-18 10:27 
-------------------------------------
'''
import asyncio
import multiprocessing

from sanic import Sanic
from sanic_ext import Extend
from loguru import logger

from config.constant import APP_NAME, SECRET_KEY, QUEUE_WORKERS
from mongodb_tool.db_tool import create_unique_index_if_not_exists

from utils.mongo_tool import setup_db

app = Sanic(APP_NAME)
app.config.CORS_ALLOW_HEADERS = "*"
app.config.CORS_ORIGINS = "*"
Extend(app)
from cores.access_token_manager import AccessTokenManager
from cores.em_shop_manager import EmShopManager
app.config.SECRET = SECRET_KEY


async def worker(app):
    while True:
        logger.info("worker start。。。")
        job = await app.ctx.queue.get()
        app.add_task(job)
        await asyncio.sleep(1)


# 创建共享的Manager对象
@app.main_process_start
async def main_process_start(app):
    app.shared_ctx.cache = multiprocessing.Manager().dict()
    # AccessTokenManager()
    logger.info(f"飞书access token更新程序启动成功")
    # # 绑定mmongo
    # app.shared_ctx.mongo = setup_db()


@app.after_server_start
async def create_task_queue(app, loop):
    """创建任务队列"""
    return
    app.ctx.queue = asyncio.Queue()
    for x in range(QUEUE_WORKERS):
        app.add_task(worker(app))





async def init_db(app):
    db,db_em_data = await setup_db()
    app.ctx.mongo = db
    app.ctx.mongo_em_data = db_em_data
    logger.info(f"app 注册 mongo成功")

@app.listener("after_server_stop")
async def afterServerStop(app, loop):
    await asyncio.gather(*[task for task in asyncio.all_tasks() if task != asyncio.current_task()])
app.add_task(init_db(app))
# app.add_task(EmShopManager.loop())
app.add_task(create_unique_index_if_not_exists(app,"ean","ean_unit_index",keys=[("ean", 1), ("campanyId", 1)], unique=True))
