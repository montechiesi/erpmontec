# -*- codding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    hoje = fields.Date(string="Hoje", compute="_compute_hoje")
    montec_commitment_date = fields.Date(string="Data de entrega com tipo date")
    
    @api.depends('hoje')
    def _compute_hoje(self):
        for record in self:
            record.hoje = datetime.now().date()
            if record.commitment_date:
                record.montec_commitment_date = record.commitment_date.date()
