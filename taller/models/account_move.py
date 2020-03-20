from odoo import models, fields

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    serie_id = fields.Many2one('stock.production.lot', string="No. Serie")
    