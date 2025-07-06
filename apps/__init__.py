# -*- coding: UTF-8 -*-
"""
@Project     ：EM_ERP_BAKEN_SANIC
@File        ：__init__.py.py
@IDE         ：PyCharm
-------------------------------------
@Author      ：Coisin
@QQ          ：2849068933
@PHONE       ：17350199092
@Description ：
@Date        ：2024-11-17 18:44
-------------------------------------
"""
from sanic import Blueprint

from .ads_credit_records.ads_credit_records import bp_ads_credit_records
from .couponManager.couponManager import bp_coupon_manager
from .databoard.databoard import bp_databoard
from .em_order.em_order import bp_em_order
from .rootAnalysis.rootAnalysis import bp_root_analysis
from .user.user import bp_user
from .shop.shop import bp_shop
from .festival.festival import bp_festival
from .route.route import bp_route
from .button.button import bp_button
from .menu.menu import bp_menu
from .role.role import bp_role
from .profit_calculator_save_data.profit_calculator_save_data import bp_profit_calculator_save_data
from .config_data.config_data import bp_config_data
from .product.product import bp_product
from .supplier.supplier import bp_supplier
from .purchase_orders.purchase_orders import bp_purchase_orders
from .local_warehouse.local_warehouse import bp_local_warehouse
from .overseas_warehouse.overseas_warehouse import bp_overseas_warehouse
from .listing.listing import bp_listing
from .tasks.tasks import bp_tasks
from .images.images import bp_images
from .ean.ean import bp_ean
from .em_category.em_category import bp_em_category
from .sku_inventory_index.sku_inventory_index import bp_sku_inventory_index
from .sku_inventory_detail.sku_inventory_detail import bp_sku_inventory_detail
from .msku_inventory_index.msku_inventory_index import bp_msku_inventory_index
from .msku_inventory_detail.msku_inventory_detail import bp_msku_inventory_detail
from .em_opptunity_data.em_opptunity_data import bp_em_opptunity_data
from .order.order import bp_order
from .alipay.alipay import bp_alipayPro
from .campany.campany import bp_campany
from .gprs_laws.gprs_laws import bp_gprs_laws
from .print_template.print_template import bp_print_template
from .box_type_info.box_type_info import bp_box_type_info
from .packing_box_info.packing_box_info import bp_packing_box_info
from .em_reception.em_reception import bp_em_reception
from .em_search_by_image.em_search_by_image import bp_em_search_by_image
from .logistics_provider.logistics_provider import bp_logistics_provider
from .shipments_order.shipments_order import bp_shipments_order
from .vipPriceManager.vipPriceManager import bp_vip_price

blue_print_list = [bp_user, bp_shop, bp_festival, bp_route, bp_button, bp_menu, bp_role, bp_profit_calculator_save_data,
                   bp_config_data, bp_product, bp_supplier, bp_purchase_orders, bp_local_warehouse,
                   bp_overseas_warehouse, bp_listing, bp_tasks, bp_images, bp_ean, bp_em_category,
                   bp_sku_inventory_index, bp_sku_inventory_detail, bp_msku_inventory_index, bp_msku_inventory_detail,
                   bp_em_opptunity_data, bp_order, bp_alipayPro, bp_campany, bp_gprs_laws, bp_print_template,
                   bp_box_type_info,
                   bp_packing_box_info, bp_em_reception, bp_em_search_by_image, bp_logistics_provider,
                   bp_shipments_order, bp_em_order, bp_databoard, bp_vip_price, bp_coupon_manager,
                   bp_ads_credit_records, bp_root_analysis]

# 蓝图组
blue_print_group = Blueprint.group(*blue_print_list, url_prefix='/api')
