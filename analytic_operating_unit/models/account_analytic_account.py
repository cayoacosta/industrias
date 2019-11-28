# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    operating_unit_ids = fields.Many2many(
        comodel_name='operating.unit', string='Operating Units',
        relation='analytic_account_operating_unit_rel',
        domain="[('user_ids', '=', uid)]",
        column1='analytic_account_id',
        column2='operating_unit_id')
