# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CancelarOtrosTalleresWizard(models.TransientModel):
    _name = 'cancelar.otros.talleres.wizard'
    
    line_ids = fields.One2many("cancelar.otros.talleres.wizard.line",'wizard_id', 'Cancelar Otros Talleres')
    reparacion_id = fields.Many2one("ordenes.de.reparacion",'Orden de reparación')
    
    @api.model
    def default_get(self, fields_list):
        res = super(CancelarOtrosTalleresWizard, self).default_get(fields_list)
        reparacion_id = self._context.get('default_reparacion_id')
        if reparacion_id:
            reparacion = self.env['ordenes.de.reparacion'].browse(reparacion_id)
            lines = []
            for order in reparacion.purchase_ids:
                lines.append((0,0,{'proveedor_id' : order.partner_id.id,
                                   'purchase_id' : order.id,
                                   }),
                             )
            if lines:
                res['line_ids'] = lines 
        return res
    
    @api.multi
    def action_cancelar_otros_talleres(self):
        reparacion = self.reparacion_id
        for line in self.line_ids:
            if not line.cancelar:
                continue
            order = line.purchase_id
            if order.state not in ['draft','sent', 'cancel']:
                continue
            partner = line.proveedor_id
            order_products = order.order_line.mapped('product_id')
            to_remove_lines = reparacion.otros_talleres_ids.filtered(lambda x: x.product_id.id in order_products.ids and x.proveedor_id.id==partner.id)
            if to_remove_lines:
                to_remove_lines.unlink()
            if order.state!='cancel':
                order.button_cancel()    
            
        return True
    
class ModificarOtrosTalleresWizardLine(models.TransientModel):
    _name = 'cancelar.otros.talleres.wizard.line'
    
    wizard_id = fields.Many2one("cancelar.otros.talleres.wizard",'Wizard')
    proveedor_id = fields.Many2one("res.partner",'Proveedor',domain=[('supplier','=',True)])
    purchase_id = fields.Many2one('purchase.order', 'Pedido')
    cancelar = fields.Boolean('Cancelar')
    
    