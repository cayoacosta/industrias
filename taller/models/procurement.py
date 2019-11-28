# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockRule(models.Model):
    _inherit = 'stock.rule'
    
    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values, group_id):
        res = super(StockRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, values, group_id)
        if values.get('taller_location_id'):
            res['location_id'] = values.get('taller_location_id')
        return res
    
    def _get_custom_move_fields(self):
        res = super(StockRule, self)._get_custom_move_fields()
        if self._context.get('ordenes_de_reparacion'):
            res += ['location_id']
        return res
    
class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    ordenes_id = fields.Many2one('ordenes.de.reparacion', 'Ordenes de reparación')

