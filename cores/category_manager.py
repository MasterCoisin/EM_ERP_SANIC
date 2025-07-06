# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BACKEN 
@File        ：category_namaer.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024/4/19 11:08 
-------------------------------------
'''
from threading import Lock

from utils.models import ModelManager
from config.constant import ALPHABET, NUMBER

categories_model = ModelManager.get_model("categories", "base")


class CategoryManager():
    LEFT_ALPHA = {0: ALPHABET.copy(), 1: ALPHABET.copy(), 2: ALPHABET.copy(), 3: ALPHABET.copy()}
    CAT_TREE = []
    OPERATION_LOCK = Lock()

    @classmethod
    def form_category_tree(cls):
        cls.LEFT_ALPHA = {0: ALPHABET.copy(), 1: ALPHABET.copy(), 2: ALPHABET.copy(), 3: ALPHABET.copy()}
        data = categories_model.objects()
        levels = {0: [], 1: [], 2: [], 3: []}
        if data:
            for obj in data:
                level = obj.cat_level
                levels[level].append(obj)
                if obj.cat_id[-1] in cls.LEFT_ALPHA[level]:
                    cls.LEFT_ALPHA[level].remove(obj.cat_id[-1])
        cat_tree = {}
        for obj in levels[0]:
            cat_tree[obj.cat_id] = {
                "cat_id": obj.cat_id,
                "cat_name": obj.cat_name,
                "cat_level": obj.cat_level,
                "cat_parent_id": obj.cat_parent_id,
                "deleted": obj.deleted,
                "children": {}
            }
        for obj in levels[1]:
            cat_tree[obj.cat_id[0]]["children"][obj.cat_id[1]] = {
                "cat_id": obj.cat_id,
                "cat_name": obj.cat_name,
                "cat_level": obj.cat_level,
                "cat_parent_id": obj.cat_parent_id,
                "deleted": obj.deleted,
                "children": {}
            }
        for obj in levels[2]:
            cat_tree[obj.cat_id[0]]["children"][obj.cat_id[1]]["children"][obj.cat_id[2]] = {
                "cat_id": obj.cat_id,
                "cat_name": obj.cat_name,
                "cat_level": obj.cat_level,
                "cat_parent_id": obj.cat_parent_id,
                "deleted": obj.deleted,
                "children": {}
            }
        for obj in levels[3]:
            cat_tree[obj.cat_id[0]]["children"][obj.cat_id[1]]["children"][obj.cat_id[2]]["children"][obj.cat_id[3]] = {
                "cat_id": obj.cat_id,
                "cat_name": obj.cat_name,
                "cat_level": obj.cat_level,
                "cat_parent_id": obj.cat_parent_id,
                "deleted": obj.deleted,
                "children": {}
            }
        # cls.CAT_TREE = parse_tree(cat_tree)
        #
        cls.CAT_TREE = [{
            "cat_id": i.cat_id,
            "cat_name": i.cat_name,
            "cat_level": i.cat_level,
            "cat_parent_id": i.cat_parent_id,
            "deleted": i.deleted
        } for i in levels[0] + levels[1] + levels[2] + levels[3]]

    @classmethod
    def delete(cls, cat_id):
        try:
            with cls.OPERATION_LOCK:
                categories_model.objects(cat_id=cat_id).delete()
                categories_model.objects(cat_parent_id=cat_id).delete()
                cls.form_category_tree()
        except:
            pass

    @classmethod
    def add(cls, cat_parent_id, cat_name, cat_level):
        try:
            if cat_parent_id != "0":
                cat_id = cat_parent_id + cls.LEFT_ALPHA[cat_level + 1].pop(0)
                categories_model(cat_name=cat_name, cat_parent_id=cat_parent_id,
                                 cat_id=cat_id, cat_level=cat_level + 1).save()
            else:
                cat_id = cls.LEFT_ALPHA[cat_level + 1].pop()
                categories_model(cat_name=cat_name, cat_parent_id=cat_parent_id,
                                 cat_id=cat_id, cat_level=cat_level + 1).save()
            return {
                "cat_name": cat_name,
                "cat_parent_id": cat_parent_id,
                "cat_id": cat_id,
                "cat_level": cat_level + 1,
                "deleted": False
            }
        except:
            return {}

    @classmethod
    def edit(cls, cat_id, cat_name, deleted):
        try:
            categories_model.objects(cat_id=cat_id).update(cat_name=cat_name, deleted=deleted)
            cls.form_category_tree()
            return True
        except Exception as e:
            return False

    @classmethod
    def cate_id_to_name(cls):
        data = categories_model.objects()
        return {i.cat_id: i.cat_name for i in data}


def parse_tree(node):
    res = []
    for k, v in node.items():
        if "children" in v:
            v["children"] = parse_tree(v["children"])
            res.append(v)
        else:
            res.append(v)
    return res

# print(parse_tree({"aa":{"children": {"a":{},"b":{"children":{"c":{}}}}}}))
