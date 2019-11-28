# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID
from odoo.api import Environment


def update_operating_unit_location(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    warehouses = env['stock.warehouse'].search([])
    for warehouse in warehouses:
        operating_unit = warehouse.operating_unit_id
        parent_location = warehouse.view_location_id
        locations = env['stock.location'].search(
            [('id', 'child_of', [parent_location.id]),
             ('usage', '=', 'internal')])
        for location in locations:
            if operating_unit:
                location.write({'operating_unit_id': operating_unit.id})
    return True
