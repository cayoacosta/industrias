# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import ValidationError

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    @api.multi
    @api.constrains('purchase_line_id', 'location_id')
    def _check_purchase_order_operating_unit(self):
        for move in self:
            if not move.purchase_line_id:
                continue
            ou = move.location_id.operating_unit_id
            order_ou = move.purchase_line_id.operating_unit_id
            if ou and order_ou:
                if (ou != order_ou and move.location_id.usage not in ('supplier', 'customer')):
                    raise ValidationError(
                        _('Configuration error. The Quotation / Purchase Order '
                          'and the Move must belong to the same '
                          'Operating Unit.')
                        )