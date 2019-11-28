# -*- coding: utf-8 -*-

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # Load all unsold PO lines
    @api.onchange('purchase_id')
    def purchase_order_change(self):
        """
        Override to add Operating Unit from Purchase Order to Invoice.
        """
        if self.purchase_id and self.purchase_id.operating_unit_id:
            # Assign OU from PO to Invoice
            self.operating_unit_id = self.purchase_id.operating_unit_id.id
        return super(AccountInvoice, self).purchase_order_change()

    @api.onchange('operating_unit_id')
    def _onchange_allowed_purchase_ids(self):
        '''
        Show only the purchase orders that have the same operating unit
        '''
        result = super(AccountInvoice, self)._onchange_allowed_purchase_ids()

        result['domain']['purchase_id'] += [('operating_unit_id', '=',
                                             self.operating_unit_id.id)]
        return result
