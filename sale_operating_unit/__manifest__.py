# -*- coding: utf-8 -*-

{
    "name": "Operating Unit in Sales",
    "version": "11.0.1.1.0",
    "summary": "An operating unit (OU) is an organizational entity part of a "
               "company",
    "author": "Eficent, "
              "Serpent Consulting Services Pvt. Ltd.,"
              "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "website": "http://www.eficent.com",
    "category": "Sales Management",
    "depends": ["sale", "account_operating_unit", "sales_team_operating_unit"],
    "data": [
        "views/sale_view.xml",
        "views/sale_report_view.xml",
        "security/sale_security.xml",
    ],
    'installable': True
}
