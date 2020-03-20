from odoo import models, fields, api

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'
    
    @api.multi
    def action_view_apuntes_contables(self):
        action = self.env.ref('account.action_account_moves_all_a').read()[0]
        action['domain'] = [('serie_id', 'in', self.ids)]
        return action
    