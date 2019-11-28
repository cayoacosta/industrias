# -*- coding: utf-8 -*-

from odoo import models 

class AccountReport(models.AbstractModel):
    _inherit = 'account.report'
    
    def _set_context(self, options):
        ctx = super(AccountReport, self)._set_context(options)
        if options.get('operating_units'):
            ctx['operating_unit_ids'] = [j.get('id') for j in options.get('operating_units') if j.get('selected')]
        return ctx