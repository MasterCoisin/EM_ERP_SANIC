# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：db_list.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：查询视图
@Date        ：2024-12-19 22:00 
-------------------------------------
'''
import datetime

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorCursor
from pymongo.errors import BulkWriteError
from sanic import Sanic, Request
from config.constant import APP_NAME

app = Sanic.get_app(APP_NAME)


def get_request_base_params(request: Request) -> (int, int, list[str], dict, list[dict]):
    current_page: int = request.json.get("current_page", 1)
    page_size: int = request.json.get("page_size", 15)
    fields: list[str] = request.json.get("fields", [])
    filters: dict = request.json.get("filters", [])
    sorts: list[dict] = request.json.get("sorts", [])
    return current_page, page_size, fields, filters, sorts


def form_filter(filter: dict) -> dict:
    if filter["t"] == "regex":
        return {"$regex": filter['query'], "$options": "i"}
    if filter["t"] == "eq":
        return {"$eq": filter['value']}
    res = {}
    if filter["min"] is not None:
        res["$gte"] = filter["min"]
    if filter["max"] is not None:
        res["$lte"] = filter["max"]

    return res


def form_fields(fields: list) -> dict:
    res = {"_id": 0}
    for i in fields:
        res[i] = 1
    return res


def add_filters(collection: AsyncIOMotorCollection, fields: list, filters: dict) -> AsyncIOMotorCursor:
    return collection.find(filters, form_fields(fields=fields))


def add_sort(motor_cursor: AsyncIOMotorCursor, sorts: [dict]) -> AsyncIOMotorCursor:
    """
    添加筛选条件
    :param motor_cursor: motor 游标
    :param sorts: 排序条件 ["field":"price","t":"desc"] t:desc/asc
    :return:
    """
    if sorts:
        return motor_cursor.sort([(s["field"], 1 if s["t"] == "asc" else -1) for s in sorts])
    return motor_cursor


def add_pagination(motor_cursor: AsyncIOMotorCursor, current_page: int = 1,
                   page_size: int = 15) -> AsyncIOMotorCursor:
    """
    分页
    :param motor_cursor: motor 游标
    :param current_page: 1
    :param page_size: 15
    :return:
    """
    return motor_cursor.skip((current_page - 1) * page_size).limit(page_size)


async def mongodb_list(collection_name: str, fields=None, filters=None, sorts=None, current_page: int = 1,
                       page_size: int = 15, seleted_shop=None,is_opp_db=False) -> [dict]:
    """
    查询视图,提供基础分页,筛选排序查询
    :param collection_name: 集合名称
    :param fields: 所需字段 如["shop_id","shop_name"]
    :param filters: 过滤条件 如[{"field":"price","min":123,"max":321,"t":"range","query":""}] t:range/regex
    :param sorts: 排序条件 [{"field":"price","t":"desc"}] t:desc/asc
    :param current_page: 1
    :param page_size: 15
    :return:
    """
    if sorts is None:
        sorts = []
    if fields is None:
        fields = []
    if filters is None:
        filters = []
    if not is_opp_db:
        collection: AsyncIOMotorCollection = app.ctx.mongo[collection_name]
    else:
        collection: AsyncIOMotorCollection = app.ctx.mongo_em_data[collection_name]
    filter_condition = {f["field"]: form_filter(filter=f) for f in filters}
    if seleted_shop:
        filter_condition["shop"] = {"$eq": seleted_shop}
    count = await collection.count_documents(filter_condition)
    motor_cursor = add_filters(collection, fields, filter_condition)
    motor_cursor = add_sort(motor_cursor, sorts=sorts)  # 排序
    motor_cursor = add_pagination(motor_cursor, current_page=current_page, page_size=page_size)  # 分页
    documents = []
    for document in await motor_cursor.to_list(length=page_size):
        for k in ["createTime", "updateTime"]:
            if k in document:
                document[k] = document[k].timestamp()
        documents.append(document)
    return {"data": documents, "total": count}


async def mongodb_create(collection_name: str, data: dict, uni_field: list) -> (bool, str):
    """
    添加数据
    :param collection_name: 集合名称
    :param data: 数据
    :param uni_field: 唯一键
    :return:
    """
    data["createTime"] = datetime.datetime.now()
    data["updateTime"] = datetime.datetime.now()
    collection: AsyncIOMotorCollection = app.ctx.mongo[collection_name]
    if uni_field:
        document = await collection.count_documents(filter={f: {"$eq": data[f]} for f in uni_field})
        if document:
            return False, "数据重复,添加失败"
    await collection.insert_one(data)
    return True, "OK"


async def batch_insert_skip_existing(
        collection: AsyncIOMotorCollection,
        documents: list[dict],
        ordered: bool = False
) -> dict:
    """
    批量插入文档，跳过已存在的数据
    :param collection: MongoDB 集合
    :param documents: 要插入的文档列表
    :param ordered: 是否按顺序插入（设为 False 可提升性能）
    :return: 包含 inserted_count（成功数）和 duplicates_count（重复数）的字典
    """
    try:
        # 批量插入操作（自动跳过重复文档）
        result = await collection.insert_many(
            documents,
            ordered=ordered
        )
        return {
            "inserted_count": len(result.inserted_ids),
            "duplicates_count": 0
        }

    except BulkWriteError as e:
        # 统计重复的文档数量
        duplicates = sum(
            1 for err in e.details["writeErrors"]
            if err["code"] == 11000  # 重复键错误代码
        )
        return {
            "inserted_count": e.details["nInserted"],
            "duplicates_count": duplicates
        }


async def mongodb_create_batch(collection_name: str, datas: list, uni_field: list) -> (bool, str):
    """
    添加数据
    :param collection_name: 集合名称
    :param datas: 数据
    :param uni_field: 唯一键
    :return:
    """
    for data in datas:
        data["createTime"] = datetime.datetime.now()
        data["updateTime"] = datetime.datetime.now()
    collection: AsyncIOMotorCollection = app.ctx.mongo[collection_name]
    result = await batch_insert_skip_existing(collection,datas)
    return True, f"成功插入 {result['inserted_count']} 条，跳过 {result['duplicates_count']} 条重复"


async def mongodb_update(collection_name: str, data: dict, uni_field: list) -> (bool, str):
    """
    添加数据
    :param collection_name: 集合名称
    :param data: 数据
    :param uni_field: 唯一键
    :return:
    """
    if "createTime" in data:
        del data["createTime"]
    data["updateTime"] = datetime.datetime.now()
    collection: AsyncIOMotorCollection = app.ctx.mongo[collection_name]
    if uni_field:
        await collection.update_one({f: {"$eq": data[f]} for f in uni_field},
                                    {"$set": {k: v for k, v in data.items() if not k.startswith("_")}})
        return True, "OK"
    return False, "请输入key"
