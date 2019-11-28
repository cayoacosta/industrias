# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    @api.depends('vehiculos_ids')
    def _compute_vehiculos(self):
        for partner in self:
            partner.vehiculos_count = len(partner.vehiculos_ids)
            
    mecanico = fields.Boolean("Mecanico")
    
    vehiculos_count = fields.Integer(string='# of vehiculos', compute='_compute_vehiculos', readonly=True)
    vehiculos_ids = fields.One2many("taller.vehiculos", 'partner_id',string='Vehiculos', readonly=True, copy=False)
    
    @api.multi
    def action_view_vehiculos(self):
        self.ensure_one()
        action = self.env.ref("taller.action_taller_vehiculos").read()[0]
        vehiculos = self.vehiculos_ids
        if len(vehiculos) > 1:
            action['domain'] = [('id', 'in', vehiculos.ids)]
        elif len(vehiculos) == 1:
            action['views'] = [(self.env.ref('taller.view_taller_vehiculos_form').id, 'form')]
            action['res_id'] = vehiculos.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action