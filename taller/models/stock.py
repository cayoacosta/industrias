# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockLocation(models.Model):
    _inherit = "stock.location"
    
    tipo = fields.Selection([('refacciones','Refacciones'),('maquinaria','Maquinaria'),('taller','Taller')],
                            string='Tipo')
    
    
class StockMove(models.Model):
    _inherit = "stock.move"
    refacciones_line_id = fields.Many2one('refacciones.ordenes.de.reparacion', 'Ordenes Line')
    in_refacciones_line_id = fields.Many2one('refacciones.ordenes.de.reparacion', 'Ordenes Line')
    created_ordernes_de_line_id = fields.Many2one('refacciones.ordenes.de.reparacion', 'Created Ordenes de Line', ondelete='set null', readonly=True, copy=False)
    
    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super(StockMove, self)._prepare_merge_moves_distinct_fields()
        distinct_fields.append('refacciones_line_id')
        return distinct_fields

    @api.model
    def _prepare_merge_move_sort_method(self, move):
        move.ensure_one()
        keys_sorted = super(StockMove, self)._prepare_merge_move_sort_method(move)
        keys_sorted.append(move.refacciones_line_id.id)
        return keys_sorted

    def _get_related_invoices(self):
        """ Overridden from stock_account to return the customer invoices
        related to this stock move.
        """
        rslt = super(StockMove, self)._get_related_invoices()
        invoices = self.mapped('picking_id.sale_id.invoice_ids').filtered(lambda x: x.state not in ('draft', 'cancel'))
        rslt += invoices
        #rslt += invoices.mapped('refund_invoice_ids')
        return rslt

    def _assign_picking_post_process(self, new=False):
        super(StockMove, self)._assign_picking_post_process(new=new)
        if new and self.refacciones_line_id and self.refacciones_line_id.reparacion_id:
            self.picking_id.message_post_with_view(
                'mail.message_origin_link',
                values={'self': self.picking_id, 'origin': self.refacciones_line_id.reparacion_id},
                subtype_id=self.env.ref('mail.mt_note').id)
    
    def _get_new_picking_values(self):
        res = super(StockMove, self)._get_new_picking_values()
        if self._context.get('ordenes_de_reparacion'):
            if self.location_dest_id.operating_unit_id:
                res['operating_unit_id'] = self.location_dest_id.operating_unit_id.id
        return res
        
class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_custom_move_fields(self):
        fields = super(StockRule, self)._get_custom_move_fields()
        fields += ['refacciones_line_id']
        return fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    ordenes_id = fields.Many2one(related="group_id.ordenes_id", string="Ordenes de reparación", store=True, readonly=False)