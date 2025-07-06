# -*- coding: UTF-8 -*-
'''
@Project     ：小红书前后端 
@File        ：data_filter.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024/3/29 17:47 
-------------------------------------
'''
from utils.models import ModelManager

user_info_model = ModelManager.get_model("user_info", "base")


def get_filter_dict(filters,currentLevel):
    filter_ = {"currentLevel__in":currentLevel}
    for filter in filters:
        key = filter.get("key", None)
        if key:
            if filter.get("min", None) is not None:
                filter_[f"{key}__gte"] = filter.get("min", None)
            if filter.get("max", None) is not None:
                filter_[f"{key}__lte"] = filter.get("max", None)
    return filter_


def get_data(filters=None, sort_condition=None, search_text=None,page_size=50,page=0,currentLevel=[]):
    if search_text is None:
        search_text = []

    if sort_condition is None:
        sort_condition = {}
    if filters is None:
        filters = []
    if not search_text:
        filter_ = get_filter_dict(filters,currentLevel)
        if sort_condition:
            count = user_info_model.objects(**filter_).count()
            data = user_info_model.objects(**filter_).order_by(("-" + sort_condition.get(
                "field")) if sort_condition.get("type", None) == "desc" else sort_condition.get("field", None)).skip(page*page_size).limit(page_size)
            data = [i.to_mongo().to_dict() for i in data]
            for i in data:
                del i["_id"]
            return data,count
        else:
            count = user_info_model.objects(**filter_).count()
            data = user_info_model.objects(**filter_).skip(page*page_size).limit(page_size)
            data = [i.to_mongo().to_dict() for i in data]
            for i in data:
                del i["_id"]
            return data,count
    filter_ = get_filter_dict(filters,currentLevel)
    for search_text_ in search_text:
        filter_[f"{search_text_['key']}__icontains"] = search_text_['query']
    if sort_condition:
        count = user_info_model.objects(**filter_).count()
        data = user_info_model.objects(**filter_).order_by(("-" + sort_condition.get(
                "field")) if sort_condition.get("type", None) == "desc" else sort_condition.get("field", None)).skip(page*page_size).limit(page_size)
        data = [i.to_mongo().to_dict() for i in data]
        for i in data:
            del i["_id"]
        return data,count
    else:
        count = user_info_model.objects(**filter_).count()
        data = user_info_model.objects(**filter_).skip(page*page_size).limit(page_size)
        data = [i.to_mongo().to_dict() for i in data]
        for i in data:
            del i["_id"]
        return data,count
