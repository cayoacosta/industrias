from odoo import models, fields, api

class MRPProduction(models.Model):
    _inherit = 'mrp.production'
    
    cliente = fields.Many2one('res.partner', string='Cliente')
    description = fields.Char(string='Description')
    
    @api.model
    def create(self, values):
        if 'origin' in values:
            sale_id = self.env['sale.order'].search([('name', '=', values['origin'])], limit=1)
            if sale_id:
                if sale_id.partner_id:
                    values['cliente'] = sale_id.partner_id.id
                if sale_id.order_line[0].name:
                    values['description'] = sale_id.order_line[0].name
                
        return super(MRPProduction, self).create(values)
    