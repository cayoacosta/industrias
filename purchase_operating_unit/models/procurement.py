# -*- coding: utf-8 -*-

from odoo import models

class StockRule(models.Model):
    _inherit = 'stock.rule'

#    @api.multi
#    @api.constrains('purchase_line_id', 'location_id')
#    def _check_purchase_order_operating_unit(self):
#        for proc in self:
#            if not proc.purchase_line_id:
#                continue
#            ou = proc.location_id.operating_unit_id
#            order_ou = proc.purchase_line_id.operating_unit_id
#            if (ou != order_ou and
#                    proc.location_id.usage not in ('supplier', 'customer')):
#                raise ValidationError(
#                    _('Configuration error. The Quotation / Purchase Order '
#                      'and the Procurement Order must belong to the same '
#                      'Operating Unit.')
#                    )

    
    def _prepare_purchase_order(self, product_id, product_qty, product_uom, origin, values, partner):
        res = super(StockRule, self)._prepare_purchase_order(product_id, product_qty, product_uom, origin, values, partner)
        operating_unit = self.location_id.operating_unit_id
        if operating_unit:
            res.update({
                'operating_unit_id': operating_unit.id,
                'requesting_operating_unit_id': operating_unit.id
            })
        return res
