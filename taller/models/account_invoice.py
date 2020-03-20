from odoo import models, fields, api

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    serie_id = fields.Many2one('stock.production.lot', string="No. Serie")
    tipo_de_venta = fields.Selection([('refacciones', 'Refacciones'), ('maquinaria', 'Maquinaria'), ('taller','Taller'),], string='Tipo de venta')
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        domain = super(AccountInvoiceLine, self)._onchange_product_id()
        if self.product_id.tipo_de_venta == 'maquinaria':
            self.tipo_de_venta = 'maquinaria'
        return domain
    
    
class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.multi
    def action_move_create(self):
        res = super(AccountInvoice, self).action_move_create()
        for rec in self.invoice_line_ids:
            if rec.serie_id:
                move_lines = self.move_id.line_ids.filtered(lambda x:x.product_id.id == rec.product_id.id and not x.serie_id and x.quantity == rec.quantity) 
                if move_lines:
                    move_lines[0].write({'serie_id': rec.serie_id.id})
        return res
