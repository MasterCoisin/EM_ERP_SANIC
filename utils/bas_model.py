# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BACKEN 
@File        ：bas_model.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024/4/19 15:43 
-------------------------------------
'''
import json
import time
from pymongo import UpdateOne

from bson import ObjectId


class BaseModelManager():
    MODEL = None
    FIELDS = []

    @classmethod
    def list(cls, fields,order_by=None,filters = {}):
        if not order_by:
            data = cls.MODEL.objects(**filters).only(*fields)
        else:
            data = cls.MODEL.objects(**filters).order_by(order_by).only(*fields)
        if data:
            data = json.loads(data.to_json())
            for i in data:
                if "_id" in i:
                    i["_id"] = i["_id"]["$oid"]
            return data
        return []

    @classmethod
    def get(cls, query, fields):
        if "_id" in query:
            query["_id"] = ObjectId(query["_id"])
        data = cls.MODEL.objects(**query).only(*fields)
        if data:
            data = json.loads(data.to_json())
            for i in data:
                if "_id" in i:
                    i["_id"] = i["_id"]["$oid"]
            return data
        return []

    @classmethod
    def delete(cls, query):
        try:
            cls.MODEL.objects(**query).delete()
            return True
        except:
            return False

    @classmethod
    def update(cls, query, data):
        try:
            if "_id" in query:
                query["_id"] = ObjectId(query["_id"])
            data = {k: v for k, v in data.items() if k in cls.FIELDS}
            if "_id" in data:
                del data["_id"]
            cls.MODEL.objects(**query).update(**data)
            return True
        except Exception as e:
            print(e)
            return False

    @classmethod
    def add(cls, data):
        try:
            cls.MODEL(**data).save()
            return True
        except Exception as e:
            print(e)
            return False

def update_to_mongo(m, filter,data):
    try:
        bulk_operations = [
            UpdateOne(
                filter,  # 查询条件
                {'$set': data},  # 更新的字段
                upsert=True  # 设置为True表示如果没有匹配到文档则插入新文档
            )
        ]
        # 执行批量操作
        m._get_collection().bulk_write(bulk_operations, ordered=False)
    except Exception as e:
        pass