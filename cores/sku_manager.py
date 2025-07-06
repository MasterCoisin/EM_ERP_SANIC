# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BACKEN 
@File        ：sku_manager.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：sku分发和回收
@Date        ：2024-04-22 16:56 
-------------------------------------
'''
from threading import Lock

from utils.models import ModelManager


class SkuManager:
    MODEL = ModelManager.get_model("sku_warehouse", "base")
    LOCK = Lock()

    @classmethod
    def get(cls):
        try:
            with cls.LOCK:
                sku_obj = cls.MODEL.objects().first()
                sku = sku_obj.sku
                sku_obj.delete()
                return sku
        except:
            return None

    @classmethod
    def put(cls, sku):
        try:
            with cls.LOCK:
                if sku and len(sku) == 4:
                    cls.MODEL(sku=sku).save()
                return True
        except:
            return False
