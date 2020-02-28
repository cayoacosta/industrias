# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class ModificarOtrosTalleres(models.TransientModel):
    _name = 'modificar.otros.talleres.wizard'
    
    line_ids = fields.One2many("modificar.otros.talleres.wizard.line",'wizard_id', 'Modificar otros talleres')
    reparacion_id = fields.Many2one("ordenes.de.reparacion",'Orden de reparación')
    currency_id = fields.Many2one("res.currency", string="Currency", readonly=True, default=lambda self: self.env.user.company_id.currency_id)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('ordenes.de.reparacion'))
    
    @api.multi
    def action_create(self):
        po_exist = {}
        purchase_obj = self.env['purchase.order']
        po_line_obj = self.env['purchase.order.line'].sudo()
        otros_talleres_obj = self.env['otros.talleres.ordenes.de.reparacion']
        for line in self.line_ids:
            partner = line.proveedor_id
            if not partner:
                continue
            po = po_exist.get(partner)
            if not po:
                vals = self._prepare_purchase_order(partner)
                po = purchase_obj.sudo().create(vals)
                po_exist.update({partner: po})
            poline_vals = self._prepare_purchase_order_line(line,po)
            po_line_obj.create(poline_vals)
            otros_talleres_obj.create({
                                       'product_id':line.product_id.id,
                                       'name': line.name,
                                       'proveedor_id' : line.proveedor_id.id,
                                       'product_uom_qty' : line.product_uom_qty,
                                       'product_uom' : line.product_uom.id,
                                       'price_unit' : line.price_unit,
                                       'costo_proveedor' : line.costo_proveedor,
                                       'tax_id' : [(6,0,line.tax_id.ids)],
                                       'reparacion_id' : self.reparacion_id.id,
                                       'pct_percent': line.pct_percent,
                                       })
            
        return True
    
    @api.multi
    def _prepare_purchase_order_line(self, line, po):
        #product_uom = line.product_uom
        product_qty = line.product_uom_qty
        product = line.product_id
        partner = po.partner_id
        #procurement_uom_po_qty = product_uom._compute_quantity(product_qty, product.uom_po_id)
        seller = product._select_seller(
            partner_id=partner,
            quantity=product_qty,
            date=po.date_order and po.date_order.date(),
            uom_id=product.uom_po_id)

        taxes = product.supplier_taxes_id
        fpos = po.fiscal_position_id
        taxes_id = fpos.map_tax(taxes, product, seller.name) if fpos else taxes
        if taxes_id:
            taxes_id = taxes_id.filtered(lambda x: x.company_id.id == po.company_id.id)


        product_lang = product.with_context({'lang': partner.lang, 'partner_id': partner.id,})
        name = product_lang.display_name
        if product_lang.description_purchase:
            name += '\n' + product_lang.description_purchase

        date_planned = self.env['purchase.order.line']._get_date_planned(seller, po=po).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        return {
            'name': name,
            'product_qty': product_qty,
            'product_id': product.id,
            'product_uom': product.uom_po_id.id,
            'price_unit': line.costo_proveedor,
            'date_planned': date_planned,
            'taxes_id': [(6, 0, taxes_id.ids)],
            'order_id': po.id,
        }
        
    def _prepare_purchase_order(self,  partner):
        purchase_date = fields.Datetime.now()
        company = self.company_id
        fpos = self.env['account.fiscal.position'].with_context(force_company=company.id).get_fiscal_position(partner.id)
        return {
            'partner_id': partner.id,
            'picking_type_id': self.reparacion_id.warehouse_id.in_type_id.id,
            'operating_unit_id': self.reparacion_id.operating_unit_id.id,
            'company_id': company.id,
            'currency_id': partner.with_context(force_company=company.id).property_purchase_currency_id.id or self.env.user.company_id.currency_id.id,
            'origin': self.reparacion_id.name,
            'payment_term_id': partner.with_context(force_company=company.id).property_supplier_payment_term_id.id,
            'date_order': purchase_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'fiscal_position_id': fpos,
            'ordenes_id' : self.reparacion_id.id,
        }
    
class ModificarOtrosTalleresWizardLine(models.TransientModel):
    _name = 'modificar.otros.talleres.wizard.line'
    
    @api.depends('product_uom_qty', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of line.
        """
        for line in self:
            price = line.price_unit
            taxes = line.tax_id.compute_all(price, line.wizard_id.currency_id, line.product_uom_qty, product=line.product_id)
            line.update({
                #'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                #'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            
    wizard_id = fields.Many2one("modificar.otros.talleres.wizard",'Wizard')
    product_id = fields.Many2one("product.product",'Producto')
    name = fields.Text(string='Description', required=True)
    proveedor_id = fields.Many2one("res.partner",'Proveedor',domain=[('supplier','=',True)])
    product_uom_qty = fields.Float(string='Cantidad', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    price_unit = fields.Float('Precio unitario', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    costo_proveedor = fields.Float('Costo provedor', digits=dp.get_precision('Product Price'), default=0.0)
    tax_id = fields.Many2many('account.tax', string='Impuestos', domain=['|', ('active', '=', False), ('active', '=', True)])
    currency_id = fields.Many2one(related='wizard_id.currency_id', depends=['wizard_id'], store=True, string='Currency', readonly=True)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    pct_percent = fields.Float('PCT(%)')
    
    @api.onchange('pct_percent', 'costo_proveedor')
    def onchange_pct_costo(self):
        if self.pct_percent and self.costo_proveedor:
            self.price_unit = self.costo_proveedor * (1+self.pct_percent/100) 
            
    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0
        
        pricelist = self.proveedor_id.property_product_pricelist
        product = self.product_id.with_context(
            lang=self.proveedor_id.lang,
            partner=self.proveedor_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            pricelist = pricelist.id,
            uom=self.product_uom.id
        )

        result = {'domain': domain}

        name = product.get_product_multiline_description_sale() 

        vals.update(name=name)

        fpos = self.proveedor_id.property_account_position_id
        # If company_id is set, always filter taxes by the company
        taxes = self.product_id.taxes_id.filtered(lambda r: not self.wizard_id.company_id or r.company_id == self.wizard_id.company_id)
        self.tax_id = fpos.map_tax(taxes, self.product_id, self.reparacion_id.partner_id) if fpos else taxes
            
        if pricelist and self.proveedor_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(product.price, product.taxes_id, self.tax_id, self.wizard_id.company_id)
        self.update(vals)
        return result
    
#     product_id = fields.Many2one("product.product",'Description')
#     name = fields.Char("Description")
#     product_uom_qty = fields.Float(string='Cantidad', digits=dp.get_precision('Product Unit of Measure'))
#     product_uom_qty_new = fields.Float(string='Nueva Cantidad', digits=dp.get_precision('Product Unit of Measure'), default=1.0)
#     refacciones_line_id = fields.Many2one("refacciones.ordenes.de.reparacion",'Refacciones Line')