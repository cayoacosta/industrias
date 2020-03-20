# -*- coding: utf-8 -*-
{
    'name': "Taller",

    'summary': """
        Added new menu for taller""",

    'description': """

    """,

    'author': "IT Admin",
    'website': "www.itadmin.com",
    'category': '',
    'version': '12.5',
    'depends': [
        'account', 'sale_management', 'stock', 'stock_operating_unit','purchase','sale_stock','purchase_operating_unit','sale_crm'
        ],
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/menu.xml',
        'wizard/modificar_otros_talleres.xml',
        'wizard/cancelar_otros_talleres.xml',
        'views/ordenes_de_reparacion.xml',
        'views/res_partner_view.xml',
        'views/taller_vehiculos_view.xml',
        'views/product_template.xml',
        'views/operating_unit_view.xml',
        'views/sale_order_view.xml',
        'views/stock_quant_view.xml',
        'views/account_journal_view.xml',
        'views/stock_warehouse.xml',
        'views/stock_location_view.xml',
        'views/stock_picking_view.xml',
        'views/crm.xml',
        'views/account_invoice_view.xml',
        'views/account_move_view.xml',
        'views/stock_production_lot_view.xml',
        'report/ordenes_de_reparacion_report.xml',
        'data/mail_template_data.xml',
        'wizard/modificar_refacciones_view.xml',
        'wizard/mano_de_obra_wizard.xml',
        
    ],

}
