# -*- coding: UTF-8 -*-
'''
@Project     ：EM_ERP_BAKEN_SANIC 
@File        ：sr_en_spider.py
@IDE         ：PyCharm 
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：欧盟法规爬取
@Date        ：2025-04-09 15:49 
-------------------------------------
'''
from html import unescape
import pandas  as pd
import requests
from lxml import etree

def spider(page):
    url = "https://e-standard.eu/Home/ReloadStandardsPartial"
    payload = f"filters%5Bsort%5D=0&filters%5Bpage%5D={page}&filters%5BpageSize%5D=10000&filters%5BisHens%5D="
    headers = {
        'accept': 'text/html, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9,ro;q=0.8',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': '.AspNetCore.Culture=c%3Den-US%7Cuic%3Den-US; .AspNetCore.Session=CfDJ8Jmm1heJdS1FlPiqYe%2BYopKiBmjfsPsi4AncByK0DaoJha%2Fj7MSu2UZRUHrLfbRrRPlMhbeRa%2Byv1YZGtLdXrrSeH4ZwNViPnXmV5P%2BwzlUZXdrh1VcR6wyjdJB1%2FvPrMsrCX0TDUJyEqU7s%2Fs8R%2BPN12P3PukVX%2BWnDq%2F4QFtSG; _gid=GA1.2.540874821.1744184586; twk_idm_key=Z4BWGEC-xuxisL4njrVof; .AspNetCore.Antiforgery.Xu23KXBnJjo=CfDJ8Jmm1heJdS1FlPiqYe-YopKzbMSqDdfEYwm7yGOBOctE9JWsLxdqwCloRIYme59P5vnFq5jTxdNVTJgfryqEf1Nu842YEpPj7Sic3_q8CY7OqjA-XcmpHsND04OPrcotkkHyE24gx623IZq28VkKEZU; _ga=GA1.2.236554499.1744184586; _gat_gtag_UA_4138520_3=1; TawkConnectionTime=0; twk_uuid_5da8579178ab74187a5a1830=%7B%22uuid%22%3A%221.1vXPiRNYJTxA8e3n1CpvMIbFOULVsYgjv2wO8yiroKiitBXMfDD19b8MplFHBV2DpTJbuayoFR63uRHuJrX9M8AD9E8Aorqk4NPv6MQRjUCpXDErcre4Ffx%22%2C%22version%22%3A3%2C%22domain%22%3A%22e-standard.eu%22%2C%22ts%22%3A1744184668823%7D; _ga_LS55GQ3V5P=GS1.1.1744184585.1.1.1744184677.0.0.0; .AspNetCore.Culture=c%3Den-US%7Cuic%3Den-US',
        'origin': 'https://e-standard.eu',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://e-standard.eu/en/standards-catalog',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    response = requests.request("POST", url, headers=headers, data=payload,proxies={"http":"http://127.0.0.1:10809","https":"http://127.0.0.1:10809"},verify=False)
    return response.text


def parse_products(html_content):
    parser = etree.HTMLParser(remove_blank_text=True, recover=True)
    tree = etree.fromstring(html_content, parser)

    results = []

    # 遍历每个产品块
    for product in tree.xpath('//div[contains(@class, "product-list-wrapper")]'):
        # 提取标准名称
        title = product.xpath('.//h2[@class="product-title"]/a/text()')
        title = unescape(title[0].strip()).replace('&#x2B;', '+') if title else ""

        # 提取描述内容
        desc_elements = product.xpath('.//div[@class="product-desc"]//text()')
        desc = unescape(''.join(desc_elements)).strip()
        desc = ' '.join(desc.replace('\xa0', ' ').split())

        # 提取状态信息
        status = product.xpath('.//div[contains(@class, "s-status")][1]/span[contains(@class, "s-published")]/text()')
        status = status[0].strip() if status else "Unknown"

        results.append([title, desc, status])

    return results
def main():
    datas = []
    for page in range(9):
        print(page)
        resp = spider(page)
        data = parse_products(resp)
        datas+=data
    pd.DataFrame(datas,columns=["指令","指令内容描述","状态"]).to_excel("sr_en_new.xlsx", index=False)

if __name__ == '__main__':
    main()
