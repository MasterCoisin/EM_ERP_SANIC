# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：db_tool.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-04-02 14:22 
-------------------------------------
'''
from motor.motor_asyncio import AsyncIOMotorCollection


async def create_unique_index_if_not_exists(app,dn_name,index_name,keys,unique):
    """应用启动时自动检查并创建唯一索引"""
    collection: AsyncIOMotorCollection = app.ctx.mongo[dn_name]

    # 检查索引是否存在
    existing_indexes = await collection.list_indexes().to_list(length=None)
    index_exists = any(index["name"] == index_name for index in existing_indexes)

    # 不存在则创建
    if not index_exists:
        try:
            await collection.create_index(keys=keys,name=index_name,unique=unique)
        except Exception as e:
            print(f"❌ 索引创建失败: {str(e)}")
            # 这里可以抛异常终止应用启动，避免无索引导致数据问题
            raise