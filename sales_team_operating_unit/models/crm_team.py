# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CrmTeam(models.Model):

    _inherit = 'crm.team'

    operating_unit_id = fields.Many2one(
        'operating.unit', 'Operating Unit',
        default=lambda self: self.env['res.users'].operating_unit_default_get()
    )

    @api.multi
    @api.constrains('operating_unit_id', 'company_id')
    def _check_company_operating_unit(self):
        for team in self:
            if (team.company_id and team.operating_unit_id and
                    team.company_id != team.operating_unit_id.company_id):
                raise UserError(_('Configuration error, '
                                  'The Company in the Sales Team and in the '
                                  'Operating Unit must be the same.'))
