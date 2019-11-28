# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleReport(models.Model):

    _inherit = "sale.report"

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['operating_unit_id'] = ", s.operating_unit_id as operating_unit_id"
        groupby += ', s.operating_unit_id'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
    
#     def _select(self):
#         select_str = super(SaleReport, self)._select()
#         select_str += """
#             ,s.operating_unit_id
#         """
#         return select_str
# 
#     def _group_by(self):
#         group_by_str = super(SaleReport, self)._group_by()
#         group_by_str += """
#             ,s.operating_unit_id
#         """
#         return group_by_str
