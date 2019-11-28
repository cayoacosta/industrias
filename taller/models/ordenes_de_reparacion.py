# -*- coding: utf-8 -*-

from odoo import models, fields,api,_
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare
from odoo.exceptions import UserError

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class OrdenesDeReparacion(models.Model):
    _name = 'ordenes.de.reparacion'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    
    @api.depends('refacciones_ids.price_total','refacciones_ids.product_uom_qty','refacciones_ids.product_uom_qty','refacciones_ids.price_unit')
    def _amount_all_refacciones(self):
        """
        Compute the total amounts of the Refacciones.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.refacciones_ids:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed_refacciones': amount_untaxed,
                'amount_tax_refacciones': amount_tax,
                'amount_total_refacciones': amount_untaxed + amount_tax,
            })
    
    @api.depends('mano_de_obra_ids.price_total','refacciones_ids.product_uom_qty','refacciones_ids.product_uom_qty','refacciones_ids.price_unit')
    def _amount_all_mano(self):
        """
        Compute the total amounts of the Refacciones.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.mano_de_obra_ids:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed_mano': amount_untaxed,
                'amount_tax_mano': amount_tax,
                'amount_total_mano': amount_untaxed + amount_tax,
            })
    
    @api.depends('otros_talleres_ids.price_total','refacciones_ids.product_uom_qty','refacciones_ids.product_uom_qty','refacciones_ids.price_unit')
    def _amount_all_otros(self):
        """
        Compute the total amounts of the Refacciones.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.otros_talleres_ids:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed_otros': amount_untaxed,
                'amount_tax_otros': amount_tax,
                'amount_total_otros': amount_untaxed + amount_tax,
            })
            
    @api.multi
    @api.depends('amount_total_otros','amount_total_mano', 'amount_total_refacciones')
    def _compute_total_orden_de_reparacion(self):
        for order in self:
            order.total_orden_de_reparacion = order.amount_total_otros + order.amount_total_mano + order.amount_total_refacciones
    
    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()    
    
    name = fields.Char(
        string="Orden de reparación",
        copy=False,
        required=True,
        default=lambda self: _('New'),)
    partner_id = fields.Many2one("res.partner",'Cliente',domain=[('customer','=',True)])
    vehiculo_id = fields.Many2one("taller.vehiculos",'Vehiculo')
    mecanico_id = fields.Many2one("res.partner",'Mécanico',domain=[('mecanico','=',True)])
    fecha = fields.Date("Fecha")
    
    currency_id = fields.Many2one("res.currency", string="Currency", readonly=True, default=lambda self: self.env.user.company_id.currency_id)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('ordenes.de.reparacion'))
    refacciones_ids = fields.One2many('refacciones.ordenes.de.reparacion','reparacion_id', 'Refacciones', auto_join=True)
    mano_de_obra_ids = fields.One2many('mano.deobra.ordenes.de.reparacion','reparacion_id', 'Mano de obra', auto_join=True)
    otros_talleres_ids = fields.One2many('otros.talleres.ordenes.de.reparacion','reparacion_id', 'Otros talleres', auto_join=True)
    
    amount_untaxed_refacciones = fields.Monetary(string='Refacciones Untaxed Amount', store=True, readonly=True, compute='_amount_all_refacciones',track_visibility='onchange', track_sequence=5)
    amount_tax_refacciones = fields.Monetary(string='Refacciones Taxes', store=True, readonly=True, compute='_amount_all_refacciones')
    amount_total_refacciones = fields.Monetary(string='Refacciones Total', store=True, readonly=True,track_visibility='always', compute='_amount_all_refacciones', track_sequence=6)
    
    amount_untaxed_mano = fields.Monetary(string='Mano de obra Untaxed Amount', store=True, readonly=True, compute='_amount_all_mano',track_visibility='onchange', track_sequence=5)
    amount_tax_mano = fields.Monetary(string='Mano de obra Taxes', store=True, readonly=True, compute='_amount_all_mano')
    amount_total_mano = fields.Monetary(string='Mano de obra Total', store=True, readonly=True,track_visibility='always', compute='_amount_all_mano', track_sequence=6)
    
    amount_untaxed_otros = fields.Monetary(string='Otros Untaxed Amount', store=True, readonly=True, compute='_amount_all_otros',track_visibility='onchange', track_sequence=5)
    amount_tax_otros = fields.Monetary(string='Otros Taxes', store=True, readonly=True, compute='_amount_all_otros')
    amount_total_otros = fields.Monetary(string='Otros Total', store=True, readonly=True,track_visibility='always', compute='_amount_all_otros', track_sequence=6)
    
    total_orden_de_reparacion = fields.Float("Total orden de reparación",compute="_compute_total_orden_de_reparacion", readonly=True, store=True)
    note = fields.Text('Notas')
    state = fields.Selection([('Presupuestada','Presupuestada'),('Confirmada','Confirmada'), ('Cerrada','Cerrada'), ('Cancelado','Cancelado')],string='States', default='Presupuestada')
    orden_de_servicio_de_garantia = fields.Selection([('Pagada por el provedor', 'Pagada por el provedor'), ('Pagara por la empresa', 'Pagara por la empresa')], string='Orden de servicio de garantia')
    
    READONLY_STATES = {
        'Confirmada': [('readonly', True)],
        'Cerrada': [('readonly', True)],
    }
    
    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit', states=READONLY_STATES,
        string='Operating Unit', default=lambda self: (self.env['res.users'].operating_unit_default_get(self.env.uid)))
    
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    dest_location_id = fields.Many2one('stock.location', 'Ubicacion destino')
    
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, track_visibility='onchange', track_sequence=2, default=lambda self: self.env.user)
    team_id = fields.Many2one('crm.team', 'Sales Team', change_default=True, default=_get_default_team)
    procurement_group_id = fields.Many2one('procurement.group', 'Procurement Group', copy=False)
    incoming_group_id = fields.Many2one('procurement.group', 'Procurement Group', copy=False)
    picking_ids = fields.One2many('stock.picking', 'ordenes_id', string='Pickings')
    delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_picking_ids')
    
    in_picking_count = fields.Integer(compute='_compute_incoming_picking', string='Picking count', default=0, store=True)
    in_picking_ids = fields.Many2many('stock.picking', compute='_compute_incoming_picking', string='Receptions', copy=False, store=True)
    
    purchase_ids = fields.One2many('purchase.order', 'ordenes_id', string='Purchase Orders')
    purchase_count = fields.Integer(string='Purchase Orders', compute='_compute_purchase_orders', store=True)
    
    sale_order_count = fields.Integer(compute='_compute_sale_order_count', string='Sale Order Count')
    sale_order_ids = fields.One2many('sale.order', 'ordenes_id', 'Sales Order')
    
    @api.depends('sale_order_ids')
    def _compute_sale_order_count(self):
        for ordenes in self:
            ordenes.sale_order_count = len(ordenes.sale_order_ids)
            
    @api.depends('purchase_ids')
    def _compute_purchase_orders(self):
        for ordenes in self:
            ordenes.purchase_count = len(ordenes.purchase_ids)
            
    @api.depends('refacciones_ids.in_move_ids.returned_move_ids',
                 'refacciones_ids.in_move_ids.state',
                 'refacciones_ids.in_move_ids.picking_id')
    def _compute_incoming_picking(self):
        for ordenes in self:
            pickings = self.env['stock.picking']
            for line in ordenes.refacciones_ids:
                # We keep a limited scope on purpose. Ideally, we should also use move_orig_ids and
                # do some recursive search, but that could be prohibitive if not done correctly.
                moves = line.in_move_ids | line.in_move_ids.mapped('returned_move_ids')
                pickings |= moves.mapped('picking_id')
            ordenes.in_picking_ids = pickings
            ordenes.in_picking_count = len(pickings)
            
    @api.depends('picking_ids')
    def _compute_picking_ids(self):
        for ordenes in self:
            ordenes.delivery_count = len(ordenes.picking_ids)
            
    @api.onchange('user_id')
    def onchange_user_id(self):
        if self.user_id:
            self.team_id = self.env['crm.team']._get_default_team_id(self.user_id.id)
            
    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        domain = []
        if self.operating_unit_id:
            self.dest_location_id = self.operating_unit_id.dest_location_id
            self.warehouse_id = self.operating_unit_id.warehouse_id
            warehouses = self.env['stock.warehouse'].search([('operating_unit_id', '=',self.operating_unit_id.id)])
            if warehouses:
                self.warehouse_id = warehouses[0].id
                domain = {'warehouse_id': [('id','in',warehouses.ids)]}
            else:
                domain = {'warehouse_id': [('id','in',[])]}
        res = {}
        if domain:
            res['domain'] = domain
        return res
                
            
    
    @api.model
    def get_company_address(self, record):
        address = []
        if record.company_id.street:
            address.append(record.company_id.street)
        if record.company_id.street2:
            address.append(record.company_id.street2)
        if record.company_id.zip:
            address.append(record.company_id.zip)
        if record.company_id.city:
            address.append(record.company_id.city)
        
#         if record.company_id.country_id:
#             address.append(record.company_id.country_id.name)
        ', '.join(address)
        return ', '.join(address)
    
    @api.multi
    def unlink(self):
        for ordenes in self:
            if ordenes.sale_order_ids or ordenes.purchase_ids or ordenes.in_picking_ids or ordenes.picking_ids:
                raise UserError("You are not allowed to delete this document.")
        return super(OrdenesDeReparacion, self).unlink()
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = \
                self.env['ir.sequence'].next_by_code('ordenes.de.reparacion') or _('New')
        if not vals.get('fecha'):
            vals['fecha'] = fields.date.today()
            
        return super(OrdenesDeReparacion, self).create(vals)
    
    @api.multi
    def action_ordenes_de_reparacion_send(self):
        '''
        This function opens a window to compose an email, with the template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('taller', 'email_template_ordenes_de_reparacion')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': self._name,
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            #'custom_layout': "sale.mail_template_data_notification_email_sale_order",
            #'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
    
    @api.multi
    def action_view_in_purchase_orders(self):
        action = self.env.ref('purchase.purchase_form_action')
        result = action.read()[0]
        result['context'] = {}
        purchase_ids = self.mapped('purchase_ids')
        # choose the view_mode accordingly
        if not purchase_ids or len(purchase_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (purchase_ids.ids)
        elif len(purchase_ids) == 1:
            res = self.env.ref('purchase.purchase_order_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = purchase_ids.id
        return result
    
    @api.multi
    def action_view_in_picking(self):
        """ This function returns an action that display existing incoming picking orders of given ordenes ids. When only one found, show the picking immediately.
        """
        action = self.env.ref('stock.action_picking_tree_all')
        result = action.read()[0]
        # override the context to get rid of the default filtering on operation type
        result['context'] = {}
        pick_ids = self.mapped('in_picking_ids')
        # choose the view_mode accordingly
        if not pick_ids or len(pick_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids.id
        return result
    
    @api.multi
    def action_view_delivery(self):
        '''
        This function returns an action that display existing delivery orders
        of given ordenes de reparacion ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        action = self.env.ref('stock.action_picking_tree_all').read()[0]

        pickings = self.mapped('picking_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = pickings.id
        return action
    
    @api.multi
    def action_confirmar(self):
        purchase_obj = self.env['purchase.order']
        po_line_obj = self.env['purchase.order.line'].sudo()
        for ordenes in self:
            if self.warehouse_id:
                ordenes.refacciones_ids._action_launch_stock_rule()
                
                po_exist = {}
                for line in ordenes.otros_talleres_ids:
                    partner = line.proveedor_id
                    if not partner:
                        continue
                    po = po_exist.get(partner)
                    if not po:
                        vals = ordenes._prepare_purchase_order(partner)
                        po = purchase_obj.sudo().create(vals)
                        po_exist.update({partner: po})
                    poline_vals = self._prepare_purchase_order_line(line,po)
                    po_line_obj.create(poline_vals)
                
        self.write({'state':'Confirmada'})
        return True

    @api.multi
    def action_cancelar(self):
        self.write({'state':'Cancelado'})
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

#         price_unit = self.env['account.tax']._fix_tax_included_price_company(seller.price, product.supplier_taxes_id, taxes_id, po.company_id) if seller else 0.0
#         if price_unit and seller and po.currency_id and seller.currency_id != po.currency_id:
#             price_unit = seller.currency_id._convert(
#                 price_unit, po.currency_id, po.company_id, po.date_order or fields.Date.today())

        product_lang = product.with_context({
            'lang': partner.lang,
            'partner_id': partner.id,
        })
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
            #'move_dest_ids': [(4, x.id) for x in values.get('move_dest_ids', [])],
        }
        
    def _prepare_purchase_order(self,  partner):
        purchase_date = fields.Datetime.now()
        company = self.company_id
        fpos = self.env['account.fiscal.position'].with_context(force_company=company.id).get_fiscal_position(partner.id)
        return {
            'partner_id': partner.id,
            'picking_type_id': self.warehouse_id.in_type_id.id,
            'company_id': company.id,
            'currency_id': partner.with_context(force_company=company.id).property_purchase_currency_id.id or self.env.user.company_id.currency_id.id,
            'origin': self.name,
            'payment_term_id': partner.with_context(force_company=company.id).property_supplier_payment_term_id.id,
            'date_order': purchase_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'fiscal_position_id': fpos,
            'ordenes_id' : self.id,
        }
    
    @api.multi
    def action_reabrir(self):
        self.write({'state':'Confirmada'})
        return True    
    
    @api.multi
    def action_carrar(self):
        pickings = self.picking_ids.filtered(lambda x:x.state!='done')
        if pickings:
            msg = ', '.join(pickings.mapped('name'))
            msg = 'orders ' if len(pickings)>1 else 'order ' + msg
            raise UserError("La orden %s está abierta, no es posible cambiar al estado de “Cerrado”. Cierre todos los documentos de almacén primero."%(msg)) 
        self.write({'state':'Cerrada'})
        return True
    
    @api.multi
    def action_crear_venta(self):
        order_obj = self.env['sale.order']
        order_line_obj = self.env['sale.order.line']
        
        order_fields = order_obj._fields.keys()
        order_line_fields = order_line_obj._fields.keys()
        
        order_vals = order_obj.default_get(order_fields)
        warehouse = self.warehouse_id
        if not warehouse:
            warehouse  = self.env['stock.warehouse'].search([('operating_unit_id','=', self.operating_unit_id.id)], limit=1)
        if warehouse:
                order_vals.update({'warehouse_id': warehouse.id})
        order_vals.update({'operating_unit_id': self.operating_unit_id.id,'partner_id':self.partner_id.id, 'ordenes_id': self.id, 'orden_de_reparacion': True})
        new_order = order_obj.new(order_vals)
        new_order.onchange_partner_id()
        order_vals = new_order._convert_to_write({name: new_order[name] for name in new_order._cache})
        if order_vals.get('team_id'):
            team = self.env['crm.team'].browse(order_vals.get('team_id'))
            if team.operating_unit_id and team.operating_unit_id.id!=self.operating_unit_id.id:
                order_vals.update({'team_id': False})
                
            
        order_rec = order_obj.create(order_vals)
        order_rec.onchange_tipo()
        
        default_order_line_vals = order_line_obj.default_get(order_line_fields)
        for line in self.refacciones_ids:
            order_line_vals = dict(default_order_line_vals)
            order_line_vals.update({
                                    'order_id' : order_rec.id,
                                    'product_id': line.product_id.id,
                                    })
            new_order_line = order_line_obj.new(order_line_vals)
            new_order_line.product_id_change()
            order_line_vals = new_order_line._convert_to_write({name: new_order_line[name] for name in new_order_line._cache})
            order_line_vals.update({'name': line.name, 'price_unit': line.price_unit, 'product_uom_qty': line.product_uom_qty, 'product_uom': line.product_uom.id, 'tax_id': [(6,0,line.tax_id.ids)]})
            order_line_obj.create(order_line_vals)
            
        for line in self.mano_de_obra_ids:
            order_line_vals = dict(default_order_line_vals)
            order_line_vals.update({
                                    'order_id' : order_rec.id,
                                    'product_id': line.product_id.id,
                                    })
            new_order_line = order_line_obj.new(order_line_vals)
            new_order_line.product_id_change()
            order_line_vals = new_order_line._convert_to_write({name: new_order_line[name] for name in new_order_line._cache})
            order_line_vals.update({'name': line.name, 'price_unit': line.price_unit, 'product_uom_qty': line.product_uom_qty, 'product_uom': line.product_uom.id, 'tax_id': [(6,0,line.tax_id.ids)]})
            order_line_obj.create(order_line_vals)
                
        for line in self.otros_talleres_ids:
            order_line_vals = dict(default_order_line_vals)
            order_line_vals.update({
                                    'order_id' : order_rec.id,
                                    'product_id': line.product_id.id,
                                    })
            new_order_line = order_line_obj.new(order_line_vals)
            new_order_line.product_id_change()
            order_line_vals = new_order_line._convert_to_write({name: new_order_line[name] for name in new_order_line._cache})
            order_line_vals.update({'name': line.name, 'price_unit': line.price_unit, 'product_uom_qty': line.product_uom_qty, 'product_uom': line.product_uom.id, 'tax_id': [(6,0,line.tax_id.ids)]})
            order_line_obj.create(order_line_vals)
                   
        return True
    
    @api.multi
    def action_modificar_refacciones(self):
        action = self.env.ref('taller.action_modificar_refacciones_wizard').read()[0]
        #wizard_obj = self.env['modificar.refacciones']
        wizard_lines = []
        for line in self.refacciones_ids:
            wizard_lines.append({'product_id': line.product_id.id,'name':line.name, 'product_uom_qty' : line.product_uom_qty, 'product_uom_qty_new': line.product_uom_qty, 'refacciones_line_id': line.id})
#             wizard_rec = wizard_obj.create({'product_id': line.product_id.id, 'product_uom_qty' : line.product_uom_qty, 'product_uom_qty_new': line.product_uom_qty, 'refacciones_line_id': line.id})
#             wizard_ids.append(wizard_rec.id)
        
        action['context'] = {'default_line_ids': wizard_lines,'default_reparacion_id': self.id} 
        return action
    
    @api.multi
    def action_modificar_mano_de_obra(self):
        action = self.env.ref('taller.action_mano_de_obra_wizard_wizard').read()[0]
        #wizard_obj = self.env['modificar.refacciones']
        wizard_lines = []
        for line in self.mano_de_obra_ids:
            wizard_lines.append({'product_id': line.product_id.id,'name':line.name, 
                                 'mecanico_id': line.mecanico_id.id,'product_uom':line.product_uom.id,
                                 'product_uom_qty' : line.product_uom_qty, 'price_unit': line.price_unit, 
                                 'tax_id': [(6,0,line.tax_id.ids)],
                                 'mano_de_obra_line_id': line.id})
#             wizard_rec = wizard_obj.create({'product_id': line.product_id.id, 'product_uom_qty' : line.product_uom_qty, 'product_uom_qty_new': line.product_uom_qty, 'refacciones_line_id': line.id})
#             wizard_ids.append(wizard_rec.id)
        
        action['context'] = {'default_line_ids': wizard_lines,'default_reparacion_id': self.id} 
        return action
    
    @api.multi
    def _get_destination_location(self):
        self.ensure_one()
        return self.warehouse_id.in_type_id.default_location_dest_id.id
    
    @api.model
    def _prepare_incoming_picking(self):
        if not self.incoming_group_id:
            self.incoming_group_id = self.incoming_group_id.create({
                'name': self.name,
                'partner_id': self.partner_id.id
            })
        if not self.partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s") % self.partner_id.name)
        return {
            'picking_type_id': self.warehouse_id.in_type_id.id,
            'partner_id': self.partner_id.id,
            'date': self.fecha,
            'origin': self.name,
            'location_dest_id': self._get_destination_location(),
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id,
        }
        
    
class RefaccionesOrdenesDeReparacion(models.Model):
    _name = 'refacciones.ordenes.de.reparacion'
    
    @api.depends('product_uom_qty', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of line.
        """
        for line in self:
            price = line.price_unit
            taxes = line.tax_id.compute_all(price, line.reparacion_id.currency_id, line.product_uom_qty, product=line.product_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
    reparacion_id = fields.Many2one("ordenes.de.reparacion",'Orden de reparación')
    product_id = fields.Many2one("product.product",'Producto')
    name = fields.Text(string='Description', required=True)
    product_uom_qty = fields.Float(string='Cantidad', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    price_unit = fields.Float('Precio unitario', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    
    tax_id = fields.Many2many('account.tax', string='Impuestos', domain=['|', ('active', '=', False), ('active', '=', True)])
    
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)
    company_id = fields.Many2one(related='reparacion_id.company_id', string='Company', store=True, readonly=True)
    currency_id = fields.Many2one(related='reparacion_id.currency_id', depends=['reparacion_id'], store=True, string='Currency', readonly=True)
    move_ids = fields.One2many('stock.move', 'refacciones_line_id', string='Stock Moves')
    in_move_ids = fields.One2many('stock.move', 'in_refacciones_line_id', string='Incoming Stock Moves')
    route_id = fields.Many2one('stock.location.route', string='Route', domain=[('sale_selectable', '=', True)], ondelete='restrict')
    date_order = fields.Date(related='reparacion_id.fecha', string='Order Date', readonly=True)
    move_dest_ids = fields.One2many('stock.move', 'created_ordernes_de_line_id', 'Downstream Moves')
    
    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        """Retrieve the price before applying the pricelist
            :param obj product: object of current product record
            :parem float qty: total quentity of product
            :param tuple price_and_rule: tuple(price, suitable_rule) coming from pricelist computation
            :param obj uom: unit of measure of current order line
            :param integer pricelist_id: pricelist id of sales order"""
        PricelistItem = self.env['product.pricelist.item']
        field_name = 'lst_price'
        currency_id = None
        product_currency = None
        if rule_id:
            pricelist_item = PricelistItem.browse(rule_id)
            if pricelist_item.pricelist_id.discount_policy == 'without_discount':
                while pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id and pricelist_item.base_pricelist_id.discount_policy == 'without_discount':
                    price, rule_id = pricelist_item.base_pricelist_id.with_context(uom=uom.id).get_product_price_rule(product, qty, self.reparacion_id.partner_id)
                    pricelist_item = PricelistItem.browse(rule_id)

            if pricelist_item.base == 'standard_price':
                field_name = 'standard_price'
            if pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id:
                field_name = 'price'
                product = product.with_context(pricelist=pricelist_item.base_pricelist_id.id)
                product_currency = pricelist_item.base_pricelist_id.currency_id
            currency_id = pricelist_item.pricelist_id.currency_id

        product_currency = product_currency or(product.company_id and product.company_id.currency_id) or self.env.user.company_id.currency_id
        if not currency_id:
            currency_id = product_currency
            cur_factor = 1.0
        else:
            if currency_id.id == product_currency.id:
                cur_factor = 1.0
            else:
                cur_factor = currency_id._get_conversion_rate(product_currency, currency_id, self.company_id or self.env.user.company_id, self.reparacion_id.fecha or fields.Date.today())

        product_uom = self.env.context.get('uom') or product.uom_id.id
        if uom and uom.id != product_uom:
            # the unit price is in a different uom
            uom_factor = uom._compute_price(1.0, product.uom_id)
        else:
            uom_factor = 1.0

        return product[field_name] * uom_factor * cur_factor, currency_id
    
    @api.multi
    def _get_display_price(self, product):
        pricelist = self.reparacion_id.partner_id.property_product_pricelist
        if pricelist.discount_policy == 'with_discount':
            return product.with_context(pricelist=pricelist.id).price
        product_context = dict(self.env.context, partner_id=self.reparacion_id.partner_id.id, date=self.reparacion_id.fecha, uom=self.product_uom.id)

        final_price, rule_id = pricelist.with_context(product_context).get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.reparacion_id.partner_id)
        base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_uom_qty, self.product_uom, pricelist.id)
        if currency != pricelist.currency_id:
            base_price = currency._convert(
                base_price, pricelist.currency_id,
                self.reparacion_id.company_id, self.reparacion_id.fecha or fields.Date.today())
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)
    
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
        
        pricelist = self.reparacion_id.partner_id.property_product_pricelist
        product = self.product_id.with_context(
            lang=self.reparacion_id.partner_id.lang,
            partner=self.reparacion_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.reparacion_id.fecha,
            pricelist = pricelist.id,
            uom=self.product_uom.id
        )

        result = {'domain': domain}

        name = product.get_product_multiline_description_sale() 

        vals.update(name=name)

        fpos = self.reparacion_id.partner_id.property_account_position_id
        # If company_id is set, always filter taxes by the company
        taxes = self.product_id.taxes_id.filtered(lambda r: not self.company_id or r.company_id == self.company_id)
        self.tax_id = fpos.map_tax(taxes, self.product_id, self.reparacion_id.partner_id) if fpos else taxes
            
        if pricelist and self.reparacion_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)
        return result
    
    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        """ Prepare specific key for moves or other components that will be created from a stock rule
        comming from a sale order line. This method could be override in order to add other custom key that could
        be used in move/po creation.
        """
        self.ensure_one()
        values = {
            'company_id': self.reparacion_id.company_id,
            'group_id': group_id,
            #'sale_line_id': self.id,
            #'date_planned': date_planned,
            'refacciones_line_id': self.id,
            'route_ids': self.route_id,
            'warehouse_id': self.reparacion_id.warehouse_id or False,
            'partner_id': self.reparacion_id.partner_id.id,
        }
        return values
    
    def _get_qty_procurement(self):
        self.ensure_one()
        qty = 0.0
        for move in self.move_ids.filtered(lambda r: r.state != 'cancel'):
            if move.picking_code in ['outgoing', 'internal']: #Nilesh Changes for internal picking
                qty += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom, rounding_method='HALF-UP')
            elif move.picking_code == 'incoming':
                qty -= move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom, rounding_method='HALF-UP')
        return qty
    
    @api.multi
    def _action_launch_stock_rule(self):
        """
        Launch procurement group run method with required/custom fields genrated by a
        sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
        depending on the sale order line product rule.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        errors = []
        proc_group_obj = self.env['procurement.group']
        for line in self:
            if not line.product_id.type in ('consu','product'):
                continue
            qty = line._get_qty_procurement()
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue

            group_id = line.reparacion_id.procurement_group_id
            if not group_id:
                group_id = proc_group_obj.create({
                    'name': line.reparacion_id.name, 'move_type': 'direct',
                    'ordenes_id': line.reparacion_id.id,
                    'partner_id': line.reparacion_id.partner_id.id,
                })
                line.reparacion_id.procurement_group_id = group_id
            else:
                # In case the procurement group is already created and the order was
                # cancelled, we need to update certain values of the group.
                updated_vals = {}
                if group_id.partner_id != line.reparacion_id.partner_id:
                    updated_vals.update({'partner_id': line.reparacion_id.partner_id.id})
                if updated_vals:
                    group_id.write(updated_vals)

            values = line._prepare_procurement_values(group_id=group_id)
            product_qty = line.product_uom_qty - qty

            procurement_uom = line.product_uom
            quant_uom = line.product_id.uom_id
            get_param = self.env['ir.config_parameter'].sudo().get_param
            if procurement_uom.id != quant_uom.id and get_param('stock.propagate_uom') != '1':
                product_qty = line.product_uom._compute_quantity(product_qty, quant_uom, rounding_method='HALF-UP')
                procurement_uom = quant_uom

            try:
                dest_location = line.reparacion_id.dest_location_id or line.reparacion_id.operating_unit_id.dest_location_id or line.reparacion_id.partner_id.property_stock_customer
                location = line.reparacion_id.operating_unit_id.location_id or dest_location
                values.update({'location_id': location.id}) #, 'location_dest_id': dest_location.id
                rule_exist = proc_group_obj.with_context(ordenes_de_reparacion=True)._get_rule(line.product_id, dest_location, values)
                if not rule_exist:
                    self.create_procurement_rule(line.reparacion_id.warehouse_id, dest_location, location)
                proc_group_obj.with_context(ordenes_de_reparacion=True).run(line.product_id, product_qty, procurement_uom, dest_location, line.name, line.reparacion_id.name, values)
            except UserError as error:
                errors.append(error.name)
        if errors:
            raise UserError('\n'.join(errors))
        return True
    
    @api.model
    def create_procurement_rule(self, warehouse, location, location_src):
        rule_obj = self.env['stock.rule'].sudo()
        field_list = rule_obj._fields.keys()
        vals = rule_obj.default_get(field_list)
        
        route_exist = self.env['stock.location.route'].sudo().search([('warehouse_selectable','=',True), ('warehouse_ids','in', [warehouse.id])] , limit=1)
        if not route_exist:
            route_exist = self.env['stock.location.route'].sudo().search([('active','=',False),('warehouse_selectable','=',True), ('warehouse_ids','in', [warehouse.id])] , limit=1)
            if not route_exist:
                route_exist = self.env['stock.location.route'].sudo().create({
                                                                'name': '%s: Internal Transfer in 1 step'%(warehouse.name),
                                                                'warehouse_selectable' : True,
                                                                'warehouse_ids' : [(6,0,[warehouse.id])],
                                                                })
            else:
                route_exist.write({'active': True})
                
        vals.update({
                'action':'pull',
                'name' : '%s: %s --> %s'%(warehouse.code, location.name, location_src.name),
                'picking_type_id' : warehouse.int_type_id.id,
                'location_src_id': location_src.id,
                'location_id': location.id,
                'procure_method' : 'make_to_stock',
                'route_id' : route_exist.id,
                'warehouse_id' : warehouse.id,
                })
        rule = rule_obj.create(vals)
        return rule
    
    @api.multi
    def _create_or_update_picking(self):
        for line in self:
            if line.product_id.type in ('product', 'consu'):
                pickings = line.reparacion_id.in_picking_ids.filtered(lambda x: x.state not in ('done', 'cancel') and x.location_dest_id.usage in ('internal', 'transit'))
                picking = pickings and pickings[0] or False
                if not picking:
                    res = line.reparacion_id._prepare_incoming_picking()
                    picking = self.env['stock.picking'].create(res)
                move_vals = line._prepare_incoming_stock_moves(picking)
                for move_val in move_vals:
                    self.env['stock.move']\
                        .create(move_val)\
                        ._action_confirm()\
                        ._action_assign()
    
    @api.multi
    def _get_stock_move_price_unit(self):
        self.ensure_one()
        line = self[0]
        order = line.reparacion_id
        price_unit = line.price_unit
        if line.tax_id:
            price_unit = line.tax_id.with_context(round=False).compute_all(
                price_unit, currency=line.reparacion_id.currency_id, quantity=1.0, product=line.product_id, partner=line.reparacion_id.partner_id
            )['total_excluded']
        if line.product_uom.id != line.product_id.uom_id.id:
            price_unit *= line.product_uom.factor / line.product_id.uom_id.factor
        if order.currency_id != order.company_id.currency_id:
            price_unit = order.currency_id._convert(
                price_unit, order.company_id.currency_id, self.company_id, self.date_order or fields.Date.today(), round=False)
        return price_unit
    
    @api.multi
    def _prepare_incoming_stock_moves(self, picking):
        """ Prepare the stock moves data for one ordenes de line. This function returns a list of
        dictionary ready to be used in stock.move's create()
        """
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res
        qty = 0.0
        price_unit = self._get_stock_move_price_unit()
        for move in self.in_move_ids.filtered(lambda x: x.state != 'cancel' and not x.location_dest_id.usage == "supplier"):
            qty += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom, rounding_method='HALF-UP')
        warehouse = self.reparacion_id.warehouse_id
        picking_type = warehouse.in_type_id
        template = {
            # truncate to 2000 to avoid triggering index limit error
            # TODO: remove index in master?
            'name': (self.name or '')[:2000],
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'date': self.reparacion_id.fecha,
            #'date_expected': self.date_planned,
            'location_id': self.reparacion_id.partner_id.property_stock_supplier.id,
            'location_dest_id': self.reparacion_id._get_destination_location(),
            'picking_id': picking.id,
            #'partner_id': self.reparacion_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'in_refacciones_line_id': self.id,
            'company_id': self.reparacion_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': picking_type.id,
            'group_id': self.reparacion_id.incoming_group_id.id,
            'origin': self.reparacion_id.name,
            'route_ids': [(6, 0, [x.id for x in warehouse.route_ids])] or [],
            'warehouse_id': warehouse.id,
        }
        
        diff_quantity = self._context.get('force_product_qty')
        if not diff_quantity:
            diff_quantity = self.product_uom_qty - qty
        if float_compare(diff_quantity, 0.0,  precision_rounding=self.product_uom.rounding) > 0:
            quant_uom = self.product_id.uom_id
            get_param = self.env['ir.config_parameter'].sudo().get_param
            if self.product_uom.id != quant_uom.id and get_param('stock.propagate_uom') != '1':
                product_qty = self.product_uom._compute_quantity(diff_quantity, quant_uom, rounding_method='HALF-UP')
                template['product_uom'] = quant_uom.id
                template['product_uom_qty'] = product_qty
            else:
                template['product_uom_qty'] = diff_quantity
            res.append(template)
        return res
    
class ManoDeObraOrdenesDeReparacion(models.Model):
    _name = 'mano.deobra.ordenes.de.reparacion'
    
    @api.depends('product_uom_qty', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of line.
        """
        for line in self:
            price = line.price_unit
            taxes = line.tax_id.compute_all(price, line.reparacion_id.currency_id, line.product_uom_qty, product=line.product_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
    reparacion_id = fields.Many2one("ordenes.de.reparacion",'Orden de reparación')
    product_id = fields.Many2one("product.product",'Producto',domain=[('mano_de_obra','=',True)])
    mecanico_id = fields.Many2one("res.partner",'Mécanico',domain=[('mecanico','=',True)])
    name = fields.Text(string='Description', required=True)
    product_uom_qty = fields.Float(string='Cantidad', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    price_unit = fields.Float('Precio unitario', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    
    tax_id = fields.Many2many('account.tax', string='Impuestos', domain=['|', ('active', '=', False), ('active', '=', True)])
    
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)
    company_id = fields.Many2one(related='reparacion_id.company_id', string='Company', store=True, readonly=True)
    currency_id = fields.Many2one(related='reparacion_id.currency_id', depends=['reparacion_id'], store=True, string='Currency', readonly=True)
    detalle = fields.Char(string='Detalles')

    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        """Retrieve the price before applying the pricelist
            :param obj product: object of current product record
            :parem float qty: total quentity of product
            :param tuple price_and_rule: tuple(price, suitable_rule) coming from pricelist computation
            :param obj uom: unit of measure of current order line
            :param integer pricelist_id: pricelist id of sales order"""
        PricelistItem = self.env['product.pricelist.item']
        field_name = 'lst_price'
        currency_id = None
        product_currency = None
        if rule_id:
            pricelist_item = PricelistItem.browse(rule_id)
            if pricelist_item.pricelist_id.discount_policy == 'without_discount':
                while pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id and pricelist_item.base_pricelist_id.discount_policy == 'without_discount':
                    price, rule_id = pricelist_item.base_pricelist_id.with_context(uom=uom.id).get_product_price_rule(product, qty, self.reparacion_id.partner_id)
                    pricelist_item = PricelistItem.browse(rule_id)

            if pricelist_item.base == 'standard_price':
                field_name = 'standard_price'
            if pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id:
                field_name = 'price'
                product = product.with_context(pricelist=pricelist_item.base_pricelist_id.id)
                product_currency = pricelist_item.base_pricelist_id.currency_id
            currency_id = pricelist_item.pricelist_id.currency_id

        product_currency = product_currency or(product.company_id and product.company_id.currency_id) or self.env.user.company_id.currency_id
        if not currency_id:
            currency_id = product_currency
            cur_factor = 1.0
        else:
            if currency_id.id == product_currency.id:
                cur_factor = 1.0
            else:
                cur_factor = currency_id._get_conversion_rate(product_currency, currency_id, self.company_id or self.env.user.company_id, self.reparacion_id.fecha or fields.Date.today())

        product_uom = self.env.context.get('uom') or product.uom_id.id
        if uom and uom.id != product_uom:
            # the unit price is in a different uom
            uom_factor = uom._compute_price(1.0, product.uom_id)
        else:
            uom_factor = 1.0

        return product[field_name] * uom_factor * cur_factor, currency_id
    
    @api.multi
    def _get_display_price(self, product):
        pricelist = self.reparacion_id.partner_id.property_product_pricelist
        if pricelist.discount_policy == 'with_discount':
            return product.with_context(pricelist=pricelist.id).price
        product_context = dict(self.env.context, partner_id=self.reparacion_id.partner_id.id, date=self.reparacion_id.fecha, uom=self.product_uom.id)

        final_price, rule_id = pricelist.with_context(product_context).get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.reparacion_id.partner_id)
        base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_uom_qty, self.product_uom, pricelist.id)
        if currency != pricelist.currency_id:
            base_price = currency._convert(
                base_price, pricelist.currency_id,
                self.reparacion_id.company_id, self.reparacion_id.fecha or fields.Date.today())
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)
    
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
        
        pricelist = self.reparacion_id.partner_id.property_product_pricelist
        product = self.product_id.with_context(
            lang=self.reparacion_id.partner_id.lang,
            partner=self.reparacion_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.reparacion_id.fecha,
            pricelist = pricelist.id,
            uom=self.product_uom.id
        )

        result = {'domain': domain}

        name = product.get_product_multiline_description_sale() 

        vals.update(name=name)

        fpos = self.reparacion_id.partner_id.property_account_position_id
        # If company_id is set, always filter taxes by the company
        taxes = self.product_id.taxes_id.filtered(lambda r: not self.company_id or r.company_id == self.company_id)
        self.tax_id = fpos.map_tax(taxes, self.product_id, self.reparacion_id.partner_id) if fpos else taxes
            
        if pricelist and self.reparacion_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)
        return result

class OtrosTalleresOrdenesDeReparacion(models.Model):
    _name = 'otros.talleres.ordenes.de.reparacion'
    
    @api.depends('product_uom_qty', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of line.
        """
        for line in self:
            price = line.price_unit
            taxes = line.tax_id.compute_all(price, line.reparacion_id.currency_id, line.product_uom_qty, product=line.product_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
    reparacion_id = fields.Many2one("ordenes.de.reparacion",'Orden de reparación')
    product_id = fields.Many2one("product.product",'Producto')
    name = fields.Text(string='Description', required=True)
    proveedor_id = fields.Many2one("res.partner",'Proveedor',domain=[('supplier','=',True)])
    product_uom_qty = fields.Float(string='Cantidad', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    price_unit = fields.Float('Precio unitario', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    costo_proveedor = fields.Float('Costo provedor', digits=dp.get_precision('Product Price'), default=0.0)
    tax_id = fields.Many2many('account.tax', string='Impuestos', domain=['|', ('active', '=', False), ('active', '=', True)])

    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)
    company_id = fields.Many2one(related='reparacion_id.company_id', string='Company', store=True, readonly=True)
    currency_id = fields.Many2one(related='reparacion_id.currency_id', depends=['reparacion_id'], store=True, string='Currency', readonly=True)
    pct_percent = fields.Float('PCT(%)')
    
    @api.onchange('pct_percent', 'costo_proveedor')
    def onchange_pct_costo(self):
        if self.pct_percent and self.costo_proveedor:
            self.price_unit = self.costo_proveedor * (1+self.pct_percent/100) 
        
    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        """Retrieve the price before applying the pricelist
            :param obj product: object of current product record
            :parem float qty: total quentity of product
            :param tuple price_and_rule: tuple(price, suitable_rule) coming from pricelist computation
            :param obj uom: unit of measure of current order line
            :param integer pricelist_id: pricelist id of sales order"""
        PricelistItem = self.env['product.pricelist.item']
        field_name = 'lst_price'
        currency_id = None
        product_currency = None
        if rule_id:
            pricelist_item = PricelistItem.browse(rule_id)
            if pricelist_item.pricelist_id.discount_policy == 'without_discount':
                while pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id and pricelist_item.base_pricelist_id.discount_policy == 'without_discount':
                    price, rule_id = pricelist_item.base_pricelist_id.with_context(uom=uom.id).get_product_price_rule(product, qty, self.reparacion_id.partner_id)
                    pricelist_item = PricelistItem.browse(rule_id)

            if pricelist_item.base == 'standard_price':
                field_name = 'standard_price'
            if pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id:
                field_name = 'price'
                product = product.with_context(pricelist=pricelist_item.base_pricelist_id.id)
                product_currency = pricelist_item.base_pricelist_id.currency_id
            currency_id = pricelist_item.pricelist_id.currency_id

        product_currency = product_currency or(product.company_id and product.company_id.currency_id) or self.env.user.company_id.currency_id
        if not currency_id:
            currency_id = product_currency
            cur_factor = 1.0
        else:
            if currency_id.id == product_currency.id:
                cur_factor = 1.0
            else:
                cur_factor = currency_id._get_conversion_rate(product_currency, currency_id, self.company_id or self.env.user.company_id, self.reparacion_id.fecha or fields.Date.today())

        product_uom = self.env.context.get('uom') or product.uom_id.id
        if uom and uom.id != product_uom:
            # the unit price is in a different uom
            uom_factor = uom._compute_price(1.0, product.uom_id)
        else:
            uom_factor = 1.0

        return product[field_name] * uom_factor * cur_factor, currency_id
    
    @api.multi
    def _get_display_price(self, product):
        pricelist = self.reparacion_id.partner_id.property_product_pricelist
        if pricelist.discount_policy == 'with_discount':
            return product.with_context(pricelist=pricelist.id).price
        product_context = dict(self.env.context, partner_id=self.reparacion_id.partner_id.id, date=self.reparacion_id.fecha, uom=self.product_uom.id)

        final_price, rule_id = pricelist.with_context(product_context).get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.reparacion_id.partner_id)
        base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_uom_qty, self.product_uom, pricelist.id)
        if currency != pricelist.currency_id:
            base_price = currency._convert(
                base_price, pricelist.currency_id,
                self.reparacion_id.company_id, self.reparacion_id.fecha or fields.Date.today())
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)
    
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
        
        pricelist = self.reparacion_id.partner_id.property_product_pricelist
        product = self.product_id.with_context(
            lang=self.reparacion_id.partner_id.lang,
            partner=self.reparacion_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.reparacion_id.fecha,
            pricelist = pricelist.id,
            uom=self.product_uom.id
        )

        result = {'domain': domain}

        name = product.get_product_multiline_description_sale() 

        vals.update(name=name)

        fpos = self.reparacion_id.partner_id.property_account_position_id
        # If company_id is set, always filter taxes by the company
        taxes = self.product_id.taxes_id.filtered(lambda r: not self.company_id or r.company_id == self.company_id)
        self.tax_id = fpos.map_tax(taxes, self.product_id, self.reparacion_id.partner_id) if fpos else taxes
            
        if pricelist and self.reparacion_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)
        return result
    
    
    
    
    