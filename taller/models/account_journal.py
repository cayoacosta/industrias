from odoo import models, fields

class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    tipo = fields.Selection([('refacciones','Refacciones'),('maquinaria','Maquinaria'),('taller','Taller')],
                            string='Tipo')
