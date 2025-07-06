# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：sr_en_save.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2025-04-12 14:21 
-------------------------------------
'''
import time
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from mongoengine import *
from tqdm import tqdm
import volcenginesdkcore
import volcenginesdktranslate20250301
from volcenginesdkcore.rest import ApiException

class GprsLaws(Document):
    lawId = StringField()
    lawText = StringField()
    lawTextZh = StringField()

    meta = {
        #  指定文档的集合
        'collection': 'gprs_laws',
        # 自定义集合名
        'verbose_name': 'gprs法规',
        'indexes': [
            {
                'fields': ['lawId'],
            },
            {
                'fields': ['lawText']
            }
        ],
    }
def insert_data():
    for row in tqdm(data.values.tolist()):
        GprsLaws(lawId=row[0],lawText=row[1]).save()

def trans(obj):
    translate_text_request = volcenginesdktranslate20250301.TranslateTextRequest(
        target_language="zh",
        text_list=[obj.lawText]
    )
    try:
        # 复制代码运行示例，请自行打印API返回值。
        resp = api_instance.translate_text(translate_text_request)
        a = [i.translation for i in resp.translation_list]
        if a:
            obj.lawTextZh = a[0]
            obj.save()
    except ApiException as e:
        # 复制代码运行示例，请自行打印API错误信息。
        print("Exception when calling api: %s\n" % e)
        return []
def transfer_data():
    pool = ThreadPoolExecutor(3)
    objs = GprsLaws.objects(lawTextZh=None)
    for obj in tqdm(objs):
        time.sleep(0.1)
        pool.submit(trans,obj)
    pool.shutdown(wait=True)


if __name__ == '__main__':
    connect(
        db='EM_ERP_SANIC',
        host='mongodb://swlcyx:swlcyx2019@127.0.0.1:27017/EM_ERP_SANIC?authSource=admin'
    )
    ak = "AKLTMWE0ZTQwNzFjNjdmNGIxNGFlZDQ0ZGY4ZDczN2NjNDM"
    sk = "T0dJMU5URXpZak5pWVRBNU5HUXpNR0V6TkdZMk5XTXdNR1U0TlRNelpEZw=="
    # 注意示例代码安全，代码泄漏会导致AK/SK泄漏，有极大的安全风险。
    configuration = volcenginesdkcore.Configuration()
    configuration.ak = ak
    configuration.sk = sk
    configuration.region = "cn-beijing"
    # set default configuration
    volcenginesdkcore.Configuration.set_default(configuration)
    # use global default configuration
    api_instance = volcenginesdktranslate20250301.TRANSLATE20250301Api()
    data = pd.read_excel("sr_en_new.xlsx")
    # insert_data()
    transfer_data()