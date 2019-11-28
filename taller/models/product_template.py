# -*- coding: utf-8 -*-

from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    mano_de_obra = fields.Boolean("Mano de obra", default=False)
    tipo_de_venta = fields.Selection([('refacciones', 'Refacciones'), ('maquinaria', 'Maquinaria'), ('taller','Taller'),], string='Tipo de venta')
    