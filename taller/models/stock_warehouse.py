from odoo import models, fields

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'
    
#     tipo = fields.Selection([('refacciones','Refacciones'),('maquinaria','Maquinaria'),('taller','Taller')],
#                             string='Tipo')
