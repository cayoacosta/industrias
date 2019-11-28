# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from lxml import etree

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    ordenes_id = fields.Many2one('ordenes.de.reparacion','Ordenes de reparacion')
    orden_de_reparacion = fields.Boolean('Orden de reparación')
    diario = fields.Many2one('account.journal','Diario')
    tipo = fields.Selection([('refacciones','Refacciones'),('maquinaria','Maquinaria'),('taller','Taller')],
                            string='Tipo',default='taller')
    
    @api.onchange('tipo', 'operating_unit_id')
    def onchange_tipo(self):
        if self.tipo:
            journal = self.env['account.journal'].search([('type','=','sale'),('tipo','=',self.tipo),('operating_unit_id','=',self.operating_unit_id.id)],limit=1)
            if journal:
                self.diario = journal.id
                
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq_code = 'sale.order'
            if vals.get('tipo','')=='refacciones':
                seq_code = 'sale.order.refacciones'
            elif vals.get('tipo','')=='maquinaria':
                seq_code = 'sale.order.maquinaria'
                
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(seq_code) or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code(seq_code) or _('New')
        result = super(SaleOrder, self).create(vals)
        return result
            
    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        if self.diario: 
            invoice_vals['journal_id'] = self.diario.id
        return invoice_vals        
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            tipo = self._context.get('default_tipo','')
            if not tipo:
                tipo = 'taller' 
            
            doc = etree.XML(res['fields']['order_line']['views']['tree']['arch'])
            for node in doc.xpath("//field[@name='product_id']"):
                node.set('domain', "[('tipo_de_venta', '=', '%s')]"%(tipo))
            res['fields']['order_line']['views']['tree']['arch'] = etree.tostring(doc)
            
            doc = etree.XML(res['fields']['order_line']['views']['form']['arch'])
            for node in doc.xpath("//field[@name='product_id']"):
                node.set('domain', "[('tipo_de_venta', '=', '%s')]"%(tipo))
            res['fields']['order_line']['views']['form']['arch'] = etree.tostring(doc)
            
        return res
    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id=group_id)
        if self.order_id.tipo:
            location = self.env['stock.location'].search([('tipo', '=',self.order_id.tipo), ('operating_unit_id', '=', self.operating_unit_id.id)], limit=1)
            res['taller_location_id'] = location and location.id or False
        elif self.order_id.orden_de_reparacion and self.order_id.ordenes_id:
            res['taller_location_id'] = self.order_id.operating_unit_id.dest_location_id.id or False
        
        return res
    