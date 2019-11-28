
from odoo import models, fields

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    ordenes_id = fields.Many2one('ordenes.de.reparacion','Ordenes de reparacion')