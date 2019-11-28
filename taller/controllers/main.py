# -*- coding: utf-8 -*-

from odoo.addons.web.controllers.main import Action
from odoo import http
from odoo.http import request

class ActionTaller(Action):
    @http.route()
    def load(self, action_id, additional_context=None):
        value = super(ActionTaller, self).load(action_id, additional_context)
        if value and value.get('res_model','')=='stock.quant' and 'user.operating_unit_ids.ids' in value.get('domain',''):
            try:
                value['domain'] = value['domain'].replace('user.operating_unit_ids.ids', str(request.env.user.operating_unit_ids.ids))
            except Exception:
                pass
#             try:
#                 ctx = value.get('context')
#                 ctx = eval(ctx)
#                 if 'user' not in ctx:
#                     ctx.update({'user':request.env.user})
#                     value['context']=ctx
#             except Exception:
#                 pass
        return value
