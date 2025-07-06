# -*- coding: UTF-8 -*-
'''
@Project     ：商机探测器市场数据抓取 
@File        ：models.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024/1/27 15:01 
-------------------------------------
'''
from mongoengine import DynamicDocument
from config.constant import MODEL_METAS, MODEL_METAS_OLD
from utils.dynamic_model import BaseDynamicModel


class ModelManager(object):
    MODELS = {model_name: BaseDynamicModel(model_meta=model_mete) for model_name, model_mete in MODEL_METAS.items()}
    VERSION = 20240109
    version = None

    @classmethod
    def change_version(cls, version):
        """
        切换数据库模型版本
        :param version:
        :return:
        """
        cls.VERSION = version
        [i.get_model(cls.VERSION, False) for i in cls.MODELS.values()]

    @classmethod
    def get_model(cls, model_name, version="base") -> DynamicDocument:
        if version:
            return cls.MODELS.get(model_name).get_model(version)
        return cls.MODELS.get(model_name).get_model(cls.VERSION)

class ModelManagerOld(object):
    MODELS = {model_name: BaseDynamicModel(model_meta=model_mete) for model_name, model_mete in MODEL_METAS_OLD.items()}
    VERSION = 20240109
    version = None

    @classmethod
    def change_version(cls, version):
        """
        切换数据库模型版本
        :param version:
        :return:
        """
        cls.VERSION = version
        [i.get_model(cls.VERSION, False) for i in cls.MODELS.values()]

    @classmethod
    def get_model(cls, model_name, version="base") -> DynamicDocument:
        if version:
            return cls.MODELS.get(model_name).get_model(version)
        return cls.MODELS.get(model_name).get_model(cls.VERSION)
