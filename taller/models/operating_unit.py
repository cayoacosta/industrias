
from odoo import models, fields

class OperatingUnit(models.Model):
    _inherit = 'operating.unit'
    
    dest_location_id = fields.Many2one('stock.location', 'Ubicacion taller')
    location_id = fields.Many2one('stock.location', 'Ubicacion surtido')
    warehouse_id = fields.Many2one('stock.warehouse', 'Almacen')
    garantia_empresa = fields.Many2one('account.journal', 'Garantía Empresa')
    garantia_proveedor = fields.Many2one('account.journal', 'Garantía del proveedor (CNH)')