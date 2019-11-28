# -*- coding: utf-8 -*-

{
    "name": "Analytic Operating Unit",
    "version": "12.0.1.0.0",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/operating-unit",
    "category": "Sales",
    "depends": [
        "analytic",
        "operating_unit",
    ],
    "data": [
        "security/analytic_account_security.xml",
        "views/analytic_account_view.xml",
    ],
    'installable': True,
}
