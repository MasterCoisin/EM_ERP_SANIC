# -*- coding: UTF-8 -*-
'''
@Project     ：
@File        ：constant.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024/3/28 15:57 
-------------------------------------
'''
import datetime
import os
from uuid import uuid1

from mongoengine import *

# 支付宝支付
APPID = "2021005121696985"
APP_PRIVATE_KEY_PATH = "alipayApi/config/privateKey.txt"
ALIPAY_PUBLIC_KEY_PATH = "alipayApi/config/alipayPublicCert.txt"
#
APP_NAME = "EM_ERP"
# 任务队列长度
QUEUE_WORKERS = 3
# token过期时间
EXPIRES_DELTA = 3600 * 24 * 7
#
RON_TO_RMB = 1.58
HUF_TO_RMB = 0.02
BGN_TO_RMB = 4.02
EXCHANGE = {"ro": RON_TO_RMB, "bg": BGN_TO_RMB, "hu": HUF_TO_RMB}
VAT = {"ro": 0.19, "bg": 0.2, "hu": 0.27}
COUNTRY_TO_CURRENCY = {"ro": "RON", "bg": "BGN", "hu": "HUF"}
FEISHU_CONFIG = {
    "app_id": "cli_a609cc6d357c900b",
    "app_secret": "Vk8fQUWPIvvgFVGY3XfkGbzZK1Z0nNj2"
}
# 初始用户密码
DEFAULT_PASSWORD = "walawala20240412"
# mongo连接url
MONGODB_URL = "mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin"  # "mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP?authSource=admin"
# MONGODB_URL = "mongodb://admin:swlcyx2019.@127.0.0.1:17017/admin?authSource=admin"
# MONGODB_HOST = os.environ.get("mongodb_host",
#                               f"mongodb://em_erp:swlcyx2019.@1.95.43.94:27017/EM_ERP?authSource=admin")
MONGODB_HOST = os.environ.get("mongodb_host",
                              f"mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP?authSource=admin")
MONGODB_HOST_SANIC = os.environ.get("mongodb_host",
                                    f"mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin")
SECRET_KEY = "em_erp_secret_key_to_encode_and_decode_token_cha&^dgafR%^Duygewfdffefrhcw"
# 图片上传地址前缀
# IMAGE_BASE_URL = "http://47.122.128.136:9001/api/images/get/"
IMAGE_BASE_URL = "https://www.fzwala.com/api/images/get/"
# 1688api接口地址
API_1688_HOST = "127.0.0.1"
API_1688_PORT = 9092
# 字母数字常量
ALPHABET = list("abcdefghijklmnpqrstuvwxyz")
NUMBER = list("1234567890")
MAX_LISTING_COUNT = 1000
TIP_TO_SELLER = "我下单了，能开普票需要加点的话麻烦在价格上加下，并且私聊我说下税点，不能开普票能开专票的话也麻烦加下税点并说下税点多少，如果是起购量没达到或者起购金额没达到开票要求的，麻烦私聊我说下开票要求，都不能开麻烦私聊我和我说不能开，不管能不能开，我工作时间会统一付款谢谢！"
# 数据模型
EM_ERP_DB = {
    "db": "EM_ERP",
    "host": MONGODB_HOST,
    "alias": "default"
}
EM_ERP_SANIC_DB = {
    "db": "EM_ERP_SANIC",
    "host": MONGODB_HOST_SANIC,
    "alias": "default"
}
MODEL_METAS_OLD = {
    "image_to_em_link": {
        "db": EM_ERP_DB,
        "field": {
            "source_id": StringField(),
            "url": StringField(),
            "trans": BooleanField
        },
        "meta": {
            "collection": "image_to_em_link",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['source_id'],
                    "name": "source_id"
                }
            ]
        }
    },
    "em_pnk_to_main_image_url": {
        "db": EM_ERP_DB,
        "field": {
            "pnk": StringField(),
            "url": StringField()
        },
        "meta": {
            "collection": "em_pnk_to_main_image_url",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['pnk'],
                    "name": "pnk"
                }
            ]
        }
    },
    "message_1688": {
        "db": EM_ERP_DB,
        "field": {
            "data": DictField(),
            "gmtBorn": IntField(),
            "msgId": IntField(),
            "msgType": StringField(),
            "userInfo": StringField(),
            "has_deal": BooleanField(default=False)
        },
        "meta": {
            "collection": "message_1688",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['msgId'],
                    "name": "msgId"
                },
                {
                    'fields': ['msgType'],
                    "name": "msgType"
                }
            ]
        }
    },
    "config_data": {
        "db": EM_ERP_DB,
        "field": {
            "field_name": StringField(),
            "data": DictField()
        },
        "meta": {
            "collection": "config_data",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['field_name'],
                    "name": "idx"
                }
            ]
        }
    },
    "ean_list": {
        "db": EM_ERP_DB,
        "field": {
            "ean": StringField(),
            "deleted": BooleanField(default=False)
        },
        "meta": {
            "collection": "ean_list",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['ean'],
                    "name": "idx"
                }
            ]
        }
    },
    "sku_warehouse": {
        "db": EM_ERP_DB,
        "field": {
            "sku": StringField()
        },
        "meta": {
            "collection": "sku_warehouse",
            "db_alias": "default",
            "indexes": [
            ]
        }
    },
    "profit_calculator_save_data": {
        "db": EM_ERP_DB,
        "field": {
            "product_profit_cal_data": DictField(),
            "cal_result": DictField(),
            "logistics_selector_result": DictField(),
            "info_1688": DictField(),
            "sku_info": DictField(help_text="草稿转入sku", default={"sku": None, "has_use": False}),
            "is_deleted": BooleanField(default=False),
            "create_time": IntField(help_text="创建时间")
        },
        "meta": {
            "collection": "profit_calculator_save_data",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['create_time'],
                    "name": "create_time"
                }
            ]
        }
    },
    "categories": {
        "db": EM_ERP_DB,
        "field": {
            "cat_id": StringField(),
            "cat_name": StringField(),
            "cat_level": IntField(),
            "cat_parent_id": StringField(default="0"),
            "deleted": BooleanField(default=False)
        },
        "meta": {
            "collection": "categories",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['cat_id'],
                    "name": "idx_cat_id"
                },
                {
                    'fields': ['cat_parent_id'],
                    "name": "idx_cat_parent_id"
                }
            ]
        }
    },
    "country": {
        "db": EM_ERP_DB,
        "field": {
            "country_id": StringField(),
            "country_name": StringField(),
            "short_name": StringField(),
            "deleted": BooleanField(default=False)
        },
        "meta": {
            "collection": "country",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['country_id'],
                    "name": "idx_country_id"
                },
                {
                    'fields': ['country_name'],
                    "name": "idx_country_name"
                }
            ]
        }
    },
    "platform": {
        "db": EM_ERP_DB,
        "field": {
            "platform_country": StringField(),
            "platform_id": StringField(),
            "platform_name": StringField(),
            "deleted": BooleanField(default=False)
        },
        "meta": {
            "collection": "platform",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['platform_id'],
                    "name": "idx_platform_id"
                },
                {
                    'fields': ['platform_name'],
                    "name": "idx_platformname"
                }
            ]
        }
    },
    "festival": {
        "db": EM_ERP_DB,
        "field": {
            "festival_country": StringField(),
            "festival_code": StringField(),
            "festival_name": StringField(),
            "deleted": BooleanField(default=False)
        },
        "meta": {
            "collection": "festival",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['festival_code'],
                    "name": "idx_festival_code"
                },
                {
                    'fields': ['festival_name'],
                    "name": "idx_festival_name"
                }
            ]
        }
    },
    "common_festival": {
        "db": EM_ERP_DB,
        "field": {
            "common_festival_country": StringField(),
            "common_festival_code": StringField(),
            "common_festival_name": StringField(),
            "deleted": BooleanField(default=False)
        },
        "meta": {
            "collection": "common_festival",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['common_festival_code'],
                    "name": "idx_common_festival_code"
                },
                {
                    'fields': ['common_festival_name'],
                    "name": "idx_common_festival_name"
                }
            ]
        }
    },
    "city": {
        "db": EM_ERP_DB,
        "field": {
            "city_id": IntField(),
            "parent_id": IntField(),
            "name": StringField(),
            "deleted": BooleanField(default=False)
        },
        "meta": {
            "collection": "city",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['city_id'],
                    "name": "idx_city_id"
                },
                {
                    'fields': ['parent_id'],
                    "name": "idx_parent_id"
                }
            ]
        }
    },
    "supplier": {
        "db": EM_ERP_DB,
        "field": {
            "name": StringField(help_text="供应商名称"),
            "sellerMemberId": StringField(help_text="供应商1688 id"),
            "contacts": StringField(help_text="联系人"),
            "contactInformation": StringField(help_text="联系方式"),
            "qqOrWx": StringField(help_text="QQ或微信"),
            "email": StringField(help_text="邮箱"),
            "fax": StringField(help_text="传真"),
            "tip": StringField(help_text="备注"),
            "seller_member_id": StringField(help_text="结算方式"),
            "paymentMethod": StringField(help_text="支付方式"),
            "unifiedSocialCreditCode": StringField(help_text="统一社会信用代码"),
            "paymentInformation": DictField(help_text="收款信息"),
            "url": StringField(help_text="网址"),
            "address": DictField(help_text="地址"),
            "deleted": BooleanField(default=False)
        },
        "meta": {
            "collection": "supplier",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['name'],
                    "name": "name"
                }
            ]
        }
    },
    "shop": {
        "db": EM_ERP_DB,
        "field": {
            "shop_country": StringField(),
            "shop_platform": StringField(),
            "shop_id": StringField(),
            "shop_name": StringField(),
            "company_info": DictField(),
            "rep": StringField(),
            "userInfo1688": StringField(help_text="1688买家ID"),
            "token1688": StringField(help_text="1688买家授权token"),
            "deleted": BooleanField(default=False)
        },
        "meta": {
            "collection": "shop",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['shop_id'],
                    "name": "idx_shop_id"
                },
                {
                    'fields': ['shop_platform'],
                    "name": "idx_shop_platform"
                },
                {
                    'fields': ['shop_country'],
                    "name": "idx_shop_country"
                }
            ]
        }
    },
    "product": {
        "db": EM_ERP_DB,
        "field": {
            "sku": StringField(help_text="产品sku"),
            "product_profit_cal_data": DynamicField(),
            "cal_result": DynamicField(),
            "logistics_selector_result": DynamicField(),
            "info_1688": DynamicField(),
            "product_attributes": DynamicField(),
            "deleted": BooleanField(default=False)
        },
        "meta": {
            "collection": "product",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['sku'],
                    "name": "idx_sku"
                },
                {
                    'name': 'search_idx',
                    'fields': ['$sku', '$product_profit_cal_data.product_name', '$product_profit_cal_data.sku'],
                    'default_language': 'en'
                }
            ]
        }
    },
    "listing": {
        "db": EM_ERP_DB,
        "field": {
            "base_info": DictField(help_text="listing基本信息"),
            "sku_list": ListField(help_text="组合/单品sku列表"),
            "packing_list": ListField(help_text="包装耗材列表"),
            "stored_attribute": DictField(help_text="存储属性,长宽高,包装后质量"),
            "packing_type": StringField(help_text="包装类型,纸盒、opp等"),
            "logistics_selector_result": DictField(help_text="物流商选择"),
            "product_profit_cal_data": DictField(help_text="此处仅存估价(含税)"),
            "cal_result": DictField(help_text="利润计算结果"),
            "em_sale_info": DictField(help_text="em产品信息"),
            "details": ListField(help_text="产品说明书"),
            "deleted": BooleanField(default=False)
        },
        "meta": {
            "collection": "listing",
            "db_alias": "default",
            "indexes": [
            ]
        }
    },
    "em_category": {
        "db": EM_ERP_DB,
        "field": {
            "category_id": IntField(help_text="em类目id"),
            "name_en": StringField(help_text="类目英文名称"),
            "name_ro": StringField(help_text="类目罗马尼亚名称"),
            "name_zh": StringField(help_text="类目罗马尼亚名称"),
            "is_allowed": IntField(
                help_text="指示卖家是否可以发送该类别中的产品和报价。为了请求访问一个特定的类别，您可以使用市场接口。0 = No 1 =是的。"),
            "parent_id": IntField(help_text="父级类目id"),
            "is_ean_mandatory": BooleanField(help_text="指示在保存产品时是否必须发送EAN 1=强制性 0=可选"),
            "is_warranty_mandatory": IntField(help_text="指示在保存产品时是否必须添加保修单 1=强制性 0=可选"),
            "characteristics": ListField(help_text="在类别中可用的所有特征"),
            "characteristics_in_baken": DictField(),
            "family_types": ListField(help_text="类别中可用的所有族类型的列表"),
            "level": IntField(),
            "version": IntField()
        },
        "meta": {
            "collection": "em_category",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['category_id'],
                    "name": "category_id"
                },
                {
                    'fields': ['parent_id'],
                    "name": "parent_id"
                },
                {
                    'fields': ['is_allowed'],
                    "name": "is_allowed"
                },
                {
                    'fields': ['is_ean_mandatory'],
                    "name": "is_ean_mandatory"
                },
                {
                    'fields': ['is_warranty_mandatory'],
                    "name": "is_warranty_mandatory"
                },
                {
                    'name': 'search_idx',
                    'fields': ['$name_en', '$name_ro', '$name_zh'],
                    'default_language': 'en'
                }
            ]
        }
    },
    "purchase_orders": {
        "db": EM_ERP_DB,
        "field": {
            "purchase_order_id": StringField(help_text="采购单编号(PO24050701)"),
            "status": IntField(default=0, help_text="采购单状态"),
            "orders": DictField(help_text="按供应商分组"),
            "create_time": IntField(help_text="创建时间")
        },
        "meta": {
            "collection": "purchase_orders",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['purchase_order_id'],
                    "name": "purchase_order_id"
                },
                {
                    'fields': ['status'],
                    "name": "status"
                },
                {
                    'fields': ['create_time'],
                    "name": "create_time"
                }
            ]
        }
    },
    "order_manager": {
        "db": EM_ERP_DB,
        "field": {
            "order_id": StringField(),
            "supplier_id": StringField(),
            "purchase_order_id": StringField(),
            "status": IntField(),
            "tradeInfo": DictField(),
        },
        "meta": {
            "collection": "order_manager",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['order_id'],
                    "name": "order_id"
                },
                {
                    'fields': ['supplier_id'],
                    "name": "supplier_id"
                },
                {
                    'fields': ['purchase_order_id'],
                    "name": "purchase_order_id"
                },
                {
                    'fields': ['status'],
                    "name": "status"
                }
            ]
        }
    },
    "reception_order": {
        "db": EM_ERP_DB,
        "field": {
            "reception_id": IntField(),
            "shipments_order_id": StringField(),
            "listing_data": ListField(),
            "listing_count": IntField(),
            "product_count": IntField(),
            "create_done": BooleanField(default=False),
            "has_send": BooleanField(default=False, help_text="是否发货"),
            "send_from": StringField(),
            "send_to": StringField(),
            "shop_id": StringField(default="wl"),
            "create_time": IntField(help_text="创建时间")
        },
        "meta": {
            "collection": "reception_order",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['reception_id'],
                    "name": "reception_id"
                },
                {
                    'fields': ['create_done'],
                    "name": "create_done"
                },
                {
                    'fields': ['create_time'],
                    "name": "create_time"
                }
            ]
        }
    },
    "local_warehouse": {
        "db": EM_ERP_DB,
        "field": {
            "wh_id": StringField(help_text="仓库ID"),
            "wh_name": StringField(help_text="仓库名称"),
            "sku_type_num": IntField(help_text="SKU种类数", default=0),
            "total": IntField(help_text="总量", default=0),
            "amount": FloatField(help_text="货值", default=0),
            "deleted": BooleanField(default=False)
        },
        "meta": {
            "collection": "local_warehouse",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['wh_id'],
                    "name": "wh_id"
                }
            ]
        }
    },
    "overseas_warehouse": {
        "db": EM_ERP_DB,
        "field": {
            "wh_id": StringField(help_text="仓库ID"),
            "wh_name": StringField(help_text="仓库名称"),
            "msku_type_num": IntField(help_text="MSKU种类数", default=0),
            "total": IntField(help_text="总量", default=0),
            "amount": FloatField(help_text="货值", default=0),
            "deleted": BooleanField(default=False)
        },
        "meta": {
            "collection": "overseas_warehouse",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['wh_id'],
                    "name": "wh_id"
                }
            ]
        }
    },
    "sku_inventory_index": {
        "db": EM_ERP_DB,
        "field": {
            "sku_wh_id": StringField(help_text="所属仓库ID"),
            "sku": StringField(help_text="sku"),
            "sku_name": StringField(help_text="sku名称"),
            "sku_img": StringField(help_text="主图链接"),
            "sku_total": IntField(help_text="sku库存", default=0),
            "sku_buy_times": IntField(help_text="sku采购次数", default=0),
            "sku_avg_fee": FloatField(help_text="sku平均采购成本", default=0),
            "deleted": BooleanField(default=False)
        },
        "meta": {
            "collection": "sku_inventory_index",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['sku_wh_id'],
                    "name": "sku_wh_id"
                },
                {
                    'fields': ['sku'],
                    "name": "sku"
                },
                {
                    'fields': ['sku_total'],
                    "name": "sku_total"
                },
                {
                    'fields': ['sku_buy_times'],
                    "name": "sku_buy_times"
                },
                {
                    'fields': ['sku_avg_cost'],
                    "name": "sku_avg_cost"
                },
                {
                    'name': 'search_idx',
                    'fields': ['$sku', 'sku_name'],
                    'default_language': 'en'
                }
            ]
        }
    },
    "sku_inventory_detail": {
        "db": EM_ERP_DB,
        "field": {
            "sku_wh_id": StringField(help_text="所属仓库ID"),
            "sku": StringField(help_text="sku"),
            "sku_name": StringField(help_text="sku名称"),
            "sku_img": StringField(help_text="主图链接"),
            "sku_batch_number": IntField(help_text="批次号"),
            "sku_batch_order": IntField(help_text="批次序号"),
            "sku_fee": FloatField(help_text="采购成本"),
            "sku_inbound_date": IntField(help_text="入库时间"),
            "deleted": BooleanField(default=False)
        },
        "meta": {
            "collection": "sku_inventory_detail",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['sku_wh_id'],
                    "name": "sku_wh_id"
                },
                {
                    'fields': ['sku'],
                    "name": "sku"
                },
                {
                    'fields': ['sku_batch_number'],
                    "name": "sku_batch_number"
                },
                {
                    'fields': ['sku_batch_number', 'sku_batch_order'],
                    "name": "sku_batch_number_sku_batch_order"
                }
            ]
        }
    },
    "msku_inventory_index": {
        "db": EM_ERP_DB,
        "field": {
            "msku_wh_id": StringField(help_text="所属仓库ID"),
            "msku": StringField(help_text="msku"),
            "ean": StringField(help_text="ean"),
            "pnk": StringField(help_text="pnk"),
            "msku_name": StringField(help_text="msku名称"),
            "msku_img": StringField(help_text="主图链接"),
            "msku_total": IntField(help_text="msku库存", default=0),
            "msku_send_times": IntField(help_text="msku发货次数", default=0),
            "msku_avg_fee": FloatField(help_text="msku平均成本,采购+头程", default=0),
            "msku_first_inbound_date": IntField(help_text="首次入库时间"),
            "msku_finall_inbound_date": IntField(help_text="最后入库时间"),
            "deleted": BooleanField(default=False)
        },
        "meta": {
            "collection": "msku_inventory_index",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['msku_wh_id'],
                    "name": "msku_wh_id"
                },
                {
                    'fields': ['msku'],
                    "name": "msku"
                },
                {
                    'fields': ['msku_total'],
                    "name": "msku_total"
                },
                {
                    'fields': ['msku_send_times'],
                    "name": "msku_send_times"
                },
                {
                    'fields': ['msku_avg_cost'],
                    "name": "msku_avg_cost"
                },
                {
                    'name': 'search_idx',
                    'fields': ['$msku', 'msku_name'],
                    'default_language': 'en'
                }
            ]
        }
    },
    "msku_inventory_detail": {
        "db": EM_ERP_DB,
        "field": {
            "msku_wh_id": StringField(help_text="所属仓库ID"),
            "msku": StringField(help_text="msku"),
            "ean": StringField(help_text="ean"),
            "pnk": StringField(help_text="pnk"),
            "msku_name": StringField(help_text="msku名称"),
            "msku_img": StringField(help_text="主图链接"),
            "msku_batch_number": IntField(help_text="批次号"),
            "msku_batch_order": IntField(help_text="批次序号"),
            "msku_fee": FloatField(help_text="采购成本"),
            "msku_head_fee": FloatField(help_text="头程成本"),
            "msku_buy_and_head_fee": FloatField(help_text="采购成本+头程成本"),
            "msku_inbound_date": IntField(help_text="入库时间"),
            "skus_info": ListField(),
            "status": IntField(default=0, help_text="0:在库 1:售出 2:退货消失 3:入仓丢失 4:销毁"),
            "order_id": IntField(help_text="订单号", default=None),
            "status_version": IntField(help_text="最后状态月份:202407"),
            "buy_country": StringField(),
            "deleted": BooleanField(default=False)
        },
        "meta": {
            "collection": "msku_inventory_detail",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['orderId'],
                    "name": "orderId"
                },
                {
                    'fields': ['ean'],
                    "name": "ean"
                },
                {
                    'fields': ['ean', 'statusVersion'],
                    "name": "ean_statusVersion"
                },
                {
                    'fields': ['msku', 'statusVersion'],
                    "name": "msku_statusVersion"
                },
                {
                    'fields': ['statusVersion'],
                    "name": "statusVersion"
                },
                {
                    'fields': ['msku_wh_id'],
                    "name": "msku_wh_id"
                },
                {
                    'fields': ['msku'],
                    "name": "msku"
                },
                {
                    'fields': ['msku_batch_number'],
                    "name": "msku_batch_number"
                },
                {
                    'fields': ['msku_batch_number', 'msku_batch_order'],
                    "name": "msku_batch_number_msku_batch_order"
                }
            ]
        }
    }
}
SHIPMENTS = {
    "logistics_provider": {
        "db": EM_ERP_DB,
        "field": {
            "lp_id": StringField(help_text="物流商ID"),
            "lp_name": StringField(help_text="物流商名称"),
            "lp_password": StringField(help_text="物流商登录密码"),
            "lp_token": StringField(help_text="物流商token"),
            "lp_expire_time": IntField(help_text="物流商token过期时间"),
            "deleted": BooleanField(default=False)
        },
        "meta": {
            "collection": "logistics_provider",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['lp_id'],
                    "name": "lp_id"
                }
            ]
        }
    },
    "box_type_info": {
        "db": EM_ERP_DB,
        "field": {
            "bx_id": StringField(help_text="箱子ID"),
            "bx_name": StringField(help_text="箱子名称"),
            "bx_l": FloatField(help_text="箱子长"),
            "bx_w": FloatField(help_text="箱子宽"),
            "bx_h": FloatField(help_text="箱子高"),
            "bx_weight": FloatField(help_text="箱子质量"),
            "deleted": BooleanField(default=False)
        },
        "meta": {
            "collection": "box_type_info",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['bx_id'],
                    "name": "bx_id"
                }
            ]
        }
    },
    "shipments_order": {
        "db": EM_ERP_DB,
        "field": {
            "shipments_order_id": StringField(help_text="发货单编号(SO24050701)"),
            "has_domestic_ogistics": BooleanField(default=True, help_text="是否有国内物流"),
            "status": IntField(default=0, help_text="发货单状态"),
            "mskus": DictField(help_text="发货产品"),
            "send_from": StringField(help_text="发货仓"),
            "send_to": StringField(help_text="到货仓"),
            "domestic_ogistics_info": DictField(help_text="国内物流信息"),
            "international_ogistics_info": DictField(help_text="国际物流信息"),
            "create_time": IntField(help_text="创建时间")
        },
        "meta": {
            "collection": "shipments_order",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['shipments_order_id'],
                    "name": "shipments_order_id"
                },
                {
                    'fields': ['status'],
                    "name": "status"
                },
                {
                    'fields': ['create_time'],
                    "name": "create_time"
                }
            ]
        }
    },
    "packing_box_info": {
        "db": EM_ERP_DB,
        "field": {
            "shipments_order_id": StringField(help_text="发货单编号(SO24050701)"),
            "left_mskus": DictField(help_text="剩余待装箱"),
            "mskus": DictField(),
            "packing_info": ListField(help_text="装箱信息"),
            "is_po": BooleanField(help_text="是否单纯装箱", default=False),
            "tip": StringField(),
            "create_time": IntField(),
            "version": IntField(help_text="分布式装箱校验")
        },
        "meta": {
            "collection": "packing_box_info",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['shipments_order_id'],
                    "name": "shipments_order_id"
                }
            ]
        }
    }
}
SYS_META = {
    "sys_user": {
        "db": EM_ERP_DB,
        "field": {
            'avatar_big': StringField(),
            'avatar_middle': StringField(),
            'avatar_thumb': StringField(),
            'avatar_url': 'StringField()://s3-imfile.feishucdn.com/static-resource/v1/v3_009v_9e2ab201-da83-4484-a13b-48f68d70834g~?image_size=72x72&cut_type=&quality=&format=image&sticker_format=.webp',
            'email': StringField(),
            'employee_no': StringField(),
            'en_name': StringField(),
            'enterprise_email': StringField(),
            'mobile': StringField(),
            'name': StringField(),
            'open_id': StringField(),
            'tenant_key': StringField(),
            'union_id': StringField(),
            'user_id': StringField()},
        "meta": {
            "collection": "sys_user",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['user_id'],
                    "name": "user_id"
                }
            ]
        }
    },
}
EM_PNK_RANK = {
    "em_cate_spider_data": {
        "db": EM_ERP_DB,
        "field": {
            "cate_sel_name": StringField(help_text="类目前台sel名称"),
            "datas": ListField(),
            "spider_date": IntField(help_text="时间戳")
        },
        "meta": {
            "collection": "em_cate_spider_data",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['cate_sel_name'],
                    "name": "cate_sel_name"
                }
            ]
        }
    },
    "em_pnk_rank_monitor_data": {
        "db": EM_ERP_DB,
        "field": {
            "pnk": StringField(help_text="PNK"),
            "cate_sel_name": StringField(default=None),
            "cate_name": StringField(),
            "cate_url": StringField(),
            "scm_id": IntField(),
            "newest_info": DictField(help_text="最新信息", default={}),
            "sb_rank": IntField(help_text="当前自然排名", default=None),
            "sp_rank": IntField(help_text="当前广告排名", default=None),
            "sp_score": FloatField(),
            "sb_rank_history": ListField(help_text="历史排名", default=[]),
            "sp_rank_history": ListField(help_text="历史排名", default=[]),
            "last_spider_day": IntField(help_text="最后爬取日期", default=None),
            "tip": StringField(help_text="备注"),
            "is_active": BooleanField(default=True)
        },
        "meta": {
            "collection": "em_pnk_rank_monitor_data",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['pnk'],
                    "name": "pnk"
                }
            ]
        }
    },
    "em_sp_spider_data": {
        "db": EM_ERP_DB,
        "field": {
            "scm_id": IntField(help_text="scm_id"),
            "data": ListField(),
            "spider_date": IntField(help_text="时间戳")
        },
        "meta": {
            "collection": "em_sp_spider_data",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['scm_id'],
                    "name": "scm_id"
                }
            ]
        }
    }
}
EM_API_BACKCALL = {
    "em_api_backcall_msg": {
        "db": EM_ERP_DB,
        "field": {
            "data": DictField(),
            "create_time": IntField(),
            "status": IntField(default=0)
        },
        "meta": {
            "collection": "em_api_backcall_msg",
            "db_alias": "default"
        }
    },
    "em_orders": {
        "db": EM_ERP_DB,
        "field": {
            "order_id": IntField(),
            "date": DateTimeField(),
            "total_price_rmb": FloatField(),
            "status": IntField(default=0)
        },
        "meta": {
            "collection": "em_orders",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['order_id'],
                    "name": "order_id"
                }
            ]
        }
    },
    "em_stock": {
        "db": EM_ERP_DB,
        "field": {
            "pnk": StringField(),
            "ean": StringField(),
            "stock": IntField(),
            "update_date": DateTimeField(),
            "version": IntField()
        },
        "meta": {
            "collection": "em_stock",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['pnk'],
                    "name": "pnk"
                },
                {
                    'fields': ['ean'],
                    "name": "ean"
                }
            ]
        }
    },
    "em_stock_index": {
        "db": EM_ERP_DB,
        "field": {
            "in_stock_count": IntField(),
            "in_trans_count": IntField(),
            "in_stock_msku_count": IntField(),
            "in_trans_msku_count": IntField(),
            "in_stock_mskus": DictField(),
            "in_trans_mskus": DictField(),
            "update_date": DateTimeField(),
            "version": IntField()
        },
        "meta": {
            "collection": "em_stock_index",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['update_date'],
                    "name": "update_date"
                },
                {
                    'fields': ['version'],
                    "name": "version"
                }
            ]
        }
    }
}
EM_FEE = {
    "em_sku_fee_month": {
        "db": EM_ERP_DB,
        "field": {
            "data": DictField(help_text=""),
            "version": IntField(help_text="月份"),
            "createTime": DateTimeField(default=datetime.datetime.now),
            "updateTime": DateTimeField(default=datetime.datetime.now),
            "t": IntField(default=0, help_text="0:截至当前期数据 1:当前月数据")
        },
        "meta": {
            "collection": "em_sku_fee_month",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['version'],
                    "name": "version"
                }
            ]
        }
    },
}
ACTIVITY_ASSISTANT = {
    "activity_assistant": {
        "db": EM_ERP_DB,
        "field": {
            "activity_id": StringField(default=uuid1),
            "msku": ListField(),
            "activity_info": ListField(),
            "tip": StringField(),
            "activity_type": StringField(default="优惠券活动"),  # 优惠券活动 降价活动
            "shop_id": StringField(default="wl"),
            "createdTime": DateTimeField(default=datetime.datetime.now),
            "updatedTime": DateTimeField(default=datetime.datetime.now),
        },
        "meta": {
            "collection": "activity_assistant",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['activity_id'],
                    "name": "activity_id"
                }
            ]
        }
    }
}

MODEL_METAS_OLD = {**MODEL_METAS_OLD, **SHIPMENTS, **SYS_META, **EM_PNK_RANK, **EM_API_BACKCALL, **EM_FEE,
                   **ACTIVITY_ASSISTANT}
MODEL_METAS = {
    "campany": {
        "db": EM_ERP_SANIC_DB,
        "field":
            {
                "campanyId": StringField(),
                "campanyName": StringField(),
                "expireTime": IntField(),
                "isVip": BooleanField(default=False),
            },
        "meta": {
            "collection": "campany",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['campanyId'],
                    "name": "campanyId"
                },
                {
                    'fields': ['campanyName'],
                    "name": "campanyName"
                }
            ]
        }
    },
    "shop": {
        "db": EM_ERP_SANIC_DB,
        "field":
            {"company_info": DictField(),
             "rep": DictField(),
             "shop_id": StringField(),
             "shop_name": StringField(),
             "em_login_info": DictField(),
             "campanyId": StringField(),
             "createTime": DateTimeField(),
             "updateTime": DateTimeField(),
             "deleted": BooleanField(default=False),
             },
        "meta": {
            "collection": "shop",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['shop_id'],
                    "name": "shop_id"
                },
                {
                    'fields': ['campanyId'],
                    "name": "campanyId"
                }
            ]
        }
    },
    "overseas_warehouse": {
        "db": EM_ERP_SANIC_DB,
        "field":
            {
                "campanyId": StringField(),
                "shop": StringField(),
                "whId": StringField(),
            },
        "meta": {
            "collection": "overseas_warehouse",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['campanyId', 'shop'],
                    "name": "idx"
                }
            ]
        }
    },
    "listing": {
        "db": EM_ERP_SANIC_DB,
        "field": {
            "campanyId": StringField(),
            "ean": StringField(),
            "msku": StringField(),
            "listingName": StringField(),
            "listingNameEn": StringField(),
            "images": ListField(),
            "addFee": DictField(),
            "invoiceInfo": DictField(),
            "baseInfo": DictField(),
            "emAttribute": DictField(),
            "emSaleInfo": DictField(),
            "flag": DictField(),
            "gprs": DictField(),
            "logisticsAttributes": DictField(),
            "packingList": ListField(),
            "skuList": ListField(),
            "shop": StringField(),
            "tip": StringField(),
            "competitorUrls": ListField(),
            "deleted": BooleanField(default=False),
            "createTime": DateTimeField(),
            "updateTime": DateTimeField(),
        },
        "meta": {
            "collection": "listing",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['shop'],
                    "name": "shop"
                },
                {
                    'fields': ['campanyId'],
                    "name": "campanyId"
                },
                {
                    'fields': ['ean'],
                    "name": "ean"
                },
                {
                    'fields': ['msku'],
                    "name": "msku"
                },
                {
                    'fields': ['listingName'],
                    "name": "listingName"
                }
            ]
        }
    },
    "em_orders": {
        "db": EM_ERP_SANIC_DB,
        "field": {
            "campanyId": StringField(),
            "country": StringField(),
            "shop": StringField(),
            "orderId": IntField(),
            "products": ListField(),
            "date": DateTimeField(),
            "totalPriceRmb": FloatField(),
            "status": IntField(default=0)
        },
        "meta": {
            "collection": "em_orders",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['orderId'],
                    "name": "orderId"
                }
            ]
        }
    },
    "em_orders_monitor_log": {
        "db": EM_ERP_SANIC_DB,
        "field": {
            "campanyId": StringField(),
            "shopId": StringField(),
            "country": StringField(),
            "lastModified": StringField(),
        },
        "meta": {
            "collection": "em_orders_monitor_log",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['campanyId', 'shopId', 'country'],
                    "name": "idx"
                }
            ]
        }
    },
    "images": {
        "db": EM_ERP_SANIC_DB,
        "field":
            {"sourceId": StringField(),
             "emUrl": StringField(),
             "sourceImgFile": BinaryField(),
             "thumbImgFile": BinaryField()
             },
        "meta": {
            "collection": "images",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ['sourceId'],
                    "name": "sourceId"
                }
            ]
        }
    },
    "order_modify_queue": {
        "db": EM_ERP_SANIC_DB,
        "field":
            {"campanyId": StringField(),
             "country": StringField(),
             "shop": StringField(),
             "orderId": IntField(),
             "status": IntField(help_text="0:未处理 1:已处理"),
             "modifyTime": DateTimeField()
             },
        "meta": {
            "collection": "order_modify_queue",
            "db_alias": "default",
            "indexes": [
                {
                    'fields': ["campanyId", "shop", "country", "orderId", "modified"],
                    "name": "addId"
                },
                {
                    'fields': ["status", 'modifyTime'],
                    "name": "modifyTime"
                }
            ]
        }
    },
    "msku_inventory_detail": {
        "db": EM_ERP_SANIC_DB,
        "field":
            {
                "campanyId": StringField(),
                "whId": StringField(),
                "ean": StringField(),
                "mskuBatchNumber": IntField(),
                "mskuBatchOrder": IntField(),
                "mskuFee": FloatField(),
                "mskuHeadFee": FloatField(),
                "mskuBuyAndHeadFee": FloatField(),
                "mskuInboundDate": IntField(),
                "skusInfo": ListField(),
                "status": IntField(default=0, help_text="0:在库 1:售出 2:在途 3:入仓丢失 4:销毁"),
                "buyCountry": StringField(),
                "orderId": IntField(),
                "statusVersion": IntField(),
                "tip": StringField(default="")
            },
        "meta": {
            'db_alias': 'default',
            'collection': 'msku_inventory_detail',
            "indexes": [
                {
                    'fields': ['campanyId', 'whId'],
                    "name": "whId"
                },
                {
                    'fields': ['campanyId', 'ean'],
                    "name": "ean"
                },
                {
                    'fields': ['campanyId', 'orderId', 'buyCountry'],
                    "name": "orderId_buyCountry"
                },
                {
                    'fields': ['campanyId', 'statusVersion'],
                    "name": "statusVersion"
                },
                {
                    'fields': ['campanyId', "whId", "ean", "mskuBatchNumber", "mskuBatchOrder"],
                    "name": "whId_ean_mskuBatchNumber_mskuBatchOrder"
                },
                {
                    'fields': ['campanyId', 'whId', 'ean', 'mskuBatchNumber', 'mskuBatchOrder', 'hasSend'],
                    "name": "whId_ean_mskuBatchNumber_mskuBatchOrder_hasSend"
                },
                {
                    'fields': ['campanyId', 'deleted'],
                    "name": "deleted"
                },
                {
                    'fields': ["campanyId", "whId", "buyCountry", "ean", "orderId"],
                    "name": "getOrder"
                }
            ]
        }
    },
    "msku_inventory_index": {
        "db": EM_ERP_SANIC_DB,
        "field":
            {
                "campanyId": StringField(),
                "whId": StringField(),
                "ean": StringField(),
                "mskuTotalSent": IntField(),
                "mskuLeft": IntField(),
                "mskuInTrans": IntField(),
                "mskuHasPurchased": IntField(),
                "mskuHasLosed": IntField(),
                "mskuHasDestroyed": IntField(),
                "mskuSendTimes": IntField(),
                "mskuFinallInboundDate": IntField(),
                "mskuFirstInboundDate": IntField(),
                "mskuAvgFee": FloatField(),
                "mskuTotalFee": FloatField(),
                "mskuAvgHeadFee": FloatField(),
                "mskuTotalHeadFee": FloatField(),
                "mskuAvgBuyAndHeadFee": FloatField(),
                "mskuTotalBuyAndHeadFee": FloatField()
            },
        "meta": {
            'db_alias': 'default',
            'collection': 'msku_inventory_index',
            "indexes": [
                {
                    'fields': ['campanyId', 'whId'],
                    "name": "whId"
                },
                {
                    'fields': ['campanyId', 'whId', 'ean'],
                    "name": "idx"
                },
                {
                    'fields': ['campanyId', 'ean'],
                    "name": "ean"
                },
                {
                    'fields': ['campanyId', 'deleted'],
                    "name": "deleted"
                }
            ]
        }
    },
    "ads_credit_records": {
        "db": EM_ERP_SANIC_DB,
        "field":
            {
                "campanyId": StringField(),
                "shop": StringField(),
                "country": StringField(),
                "creditId": StringField(),
                "creditStatus": StringField(),
                "creditType": StringField(),
                "sellerName": StringField(),
                "sellerLink": StringField(),
                "creditLink": StringField(),
                "activationDate": DateTimeField(),
                "expirationDate": DateTimeField(),
                "creditValue": FloatField(),
                "creditClicks": FloatField(),
                "availableCredit": FloatField()
            },
        "meta": {
            'db_alias': 'default',
            'collection': 'ads_credit_records',
            "indexes": [
                {
                    'fields': ['campanyId', 'shop', 'country', 'creditId'],
                    "name": "idx"
                },
                {
                    'fields': ['campanyId', 'shop', 'country', 'creditStatus'],
                    "name": "creditStatus"
                },
                {
                    'fields': ['campanyId', 'shop', 'country', 'creditType'],
                    "name": "creditType"
                },
                {
                    'fields': ['campanyId', 'shop', 'country', 'activation_date'],
                    "name": "activation_date"
                },
            ]
        }
    }
}

"""
            "status":IntField(default=0,help_text="0:装箱完成，待发货 1:已发国内物流 2:货代收到货 3：货代装柜 4：运输中 5：到货 6：入仓"),

"""
