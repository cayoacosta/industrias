# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    @api.multi
    @api.constrains('operating_unit_id')
    def _check_existing_so_in_wh(self):
        for rec in self:
            sales = self.env['sale.order'].search([
                ('warehouse_id', '=', rec.id),
                ('operating_unit_id', '!=', rec.operating_unit_id.id)])
            if sales:
                raise ValidationError(_(
                    'Sales Order records already exist(s) for this warehouse'
                    ' and operating unit.'))
