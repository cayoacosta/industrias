# -*- coding: utf-8 -*-

{
    "name": "Sales Team Operating Unit",
    "version": "12.0.1.1.0",
    "author": "Eficent, "
              "SerpentCS,"
              "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/operating-unit",
    "category": "Sales",
    "depends": ["sales_team", "operating_unit"],
    "data": [
        "security/crm_security.xml",
        "views/crm_team_view.xml",
    ],
    'installable': True,
}
