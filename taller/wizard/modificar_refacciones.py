# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare

class ModificarRefacciones(models.TransientModel):
    _name = 'modificar.refacciones'
    
    line_ids = fields.One2many("modificar.refacciones.wizard",'wizard_id', 'Modificar Refacciones')
    reparacion_id = fields.Many2one("ordenes.de.reparacion",'Orden de reparación')
    
    @api.multi
    def action_modify(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        refacciones_lines = self.line_ids.mapped('refacciones_line_id')
        deleted_lines = self.reparacion_id.refacciones_ids - refacciones_lines
        if deleted_lines:
            for line in deleted_lines:
                line.with_context(force_product_qty=line.product_uom_qty)._create_or_update_picking()
                #line.write({'product_uom_qty' : line.product_uom_qty_new})
                
            #deleted_lines.write({'product_uom_qty' : 0})
            #deleted_lines._action_launch_stock_rule()
            deleted_lines.unlink()
            
        for line in self.line_ids:
            if line.refacciones_line_id and float_compare(line.product_uom_qty, line.product_uom_qty_new, precision_digits=precision) == -1:
                
                line.refacciones_line_id.write({'product_uom_qty' : line.product_uom_qty_new})
                line.refacciones_line_id._action_launch_stock_rule()
                if line.product_uom_qty_new==0.0:
                    line.refacciones_line_id.unlink()
                    
            elif line.refacciones_line_id and float_compare(line.product_uom_qty, line.product_uom_qty_new, precision_digits=precision) == 1:
                product_qty = line.product_uom_qty - line.product_uom_qty_new
                line.refacciones_line_id.with_context(force_product_qty=product_qty)._create_or_update_picking()
                line.refacciones_line_id.write({'product_uom_qty' : line.product_uom_qty_new})
                if line.product_uom_qty_new==0.0:
                    line.refacciones_line_id.unlink()
            elif not line.refacciones_line_id:
                product = line.product_id
                refacciones_line = line.refacciones_line_id.new({
                    'product_id': product.id,
                    'name': line.name or product.name,
                    'reparacion_id': self.reparacion_id.id,
                    'product_uom_qty' : line.product_uom_qty_new,
                    'product_uom' : product.uom_id.id,
                    })
                refacciones_line.product_id_change()
                vals = refacciones_line._convert_to_write({name: refacciones_line[name] for name in refacciones_line._cache})
                refacciones_line = line.refacciones_line_id.create(vals)
                refacciones_line._action_launch_stock_rule()
                
        return
    
class ModificarRefaccionesWizard(models.TransientModel):
    _name = 'modificar.refacciones.wizard'
    
    wizard_id = fields.Many2one("modificar.refacciones",'Wizard')
    product_id = fields.Many2one("product.product",'Producto')
    name = fields.Text(string='Descripción')
    product_uom_qty = fields.Float(string='Cantidad', digits=dp.get_precision('Product Unit of Measure'))
    product_uom_qty_new = fields.Float(string='Nueva Cantidad', digits=dp.get_precision('Product Unit of Measure'), default=1.0)
    refacciones_line_id = fields.Many2one("refacciones.ordenes.de.reparacion",'Líneas de refacción')
    price_unit = fields.Float('Precio unitario', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    tax_id = fields.Many2many('account.tax', string='Impuestos', domain=['|', ('active', '=', False), ('active', '=', True)])
    
    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return
        vals = {}
        name = self.product_id.get_product_multiline_description_sale() 
        vals.update(name=name)
        self.update(vals)
        