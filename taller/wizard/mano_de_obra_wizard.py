# -*- coding: utf-8 -*-

from odoo import models, api, fields
from odoo.addons import decimal_precision as dp

class ManoDeObraWizard(models.TransientModel):
    _name = 'mano.de.obra.wizard'
    
    line_ids = fields.One2many("mano.de.obra.wizard.line",'wizard_id', 'Mano de obra')
    reparacion_id = fields.Many2one("ordenes.de.reparacion",'Orden de reparación')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('ordenes.de.reparacion'))
    
    @api.multi
    def action_modify(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        reparacion = self.reparacion_id
        mano_de_obras = reparacion.mano_de_obra_ids
        mano_de_obra_exist = self.line_ids.mapped('mano_de_obra_line_id')
        mano_de_obra_remove = mano_de_obras - mano_de_obra_exist
        if mano_de_obra_remove:
            mano_de_obra_remove.unlink()
            
        for line in self.line_ids:
            if line.mano_de_obra_line_id and line.product_uom_qty==0.0:
                line.mano_de_obra_line_id.unlink()
                continue 
            vals = {'product_id': line.product_id.id,'name':line.name, 
             'mecanico_id': line.mecanico_id.id, 'detalle': line.detalle,
             'product_uom_qty' : line.product_uom_qty, 'price_unit': line.price_unit, 
             'tax_id': [(6,0,line.tax_id.ids)],
             'mano_de_obra_line_id': line.id,
             'comision': line.comision}
            if line.product_uom:
                vals.update({'product_uom':line.product_uom.id})
                
            if line.mano_de_obra_line_id:
                line.mano_de_obra_line_id.write(vals)
            else:
                vals.update({'reparacion_id': reparacion.id,})
                line.mano_de_obra_line_id.create(vals)
        return
    
class ManoDeObraWizardLine(models.TransientModel):
    _name = 'mano.de.obra.wizard.line'
    
    wizard_id = fields.Many2one("mano.de.obra.wizard",'Wizard')
    
    product_id = fields.Many2one("product.product",'Producto',domain=[('mano_de_obra','=',True)])
    name = fields.Text(string='Description', required=True)
    mecanico_id = fields.Many2one("res.partner",'Mécanico',domain=[('mecanico','=',True)])
    product_uom_qty = fields.Float(string='Cantidad', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    price_unit = fields.Float('Precio unitario', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    tax_id = fields.Many2many('account.tax', string='Impuestos', domain=['|', ('active', '=', False), ('active', '=', True)])
    mano_de_obra_line_id = fields.Many2one("mano.deobra.ordenes.de.reparacion",'Mano de obra Line')
    detalle = fields.Char(string='Detalles')
    comision = fields.Float(string="Comision")
    
    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return
        vals = {}
        name = self.product_id.get_product_multiline_description_sale() 
        vals.update(name=name)
        
        fpos = self.mecanico_id.property_account_position_id
        # If company_id is set, always filter taxes by the company
        taxes = self.product_id.taxes_id.filtered(lambda r: not self.wizard_id.company_id or r.company_id == self.wizard_id.company_id)
        self.tax_id = fpos.map_tax(taxes, self.product_id, self.wizard_id.reparacion_id.partner_id) if fpos else taxes
        
        self.update(vals)