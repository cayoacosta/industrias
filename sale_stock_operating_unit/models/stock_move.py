# -*- coding: utf-8 -*-

from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_new_picking_values(self):
        """
        Override to add Operating Units to Picking.
        """
        values = super(StockMove, self)._get_new_picking_values()
        sale_line = self.sale_line_id #and self.procurement_id.sale_line_id
        if sale_line:
            values.update({
                'operating_unit_id': sale_line.order_id and
                sale_line.order_id.operating_unit_id.id
            })
        return values
