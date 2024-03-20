# -*- codding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api

class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    def _compute_diference_days(self):
        for record in self:
            if record.scheduled_date:
                diference = (record.scheduled_date - record.create_date).days
                record.diference_days = diference
            else:
                record.diference_days = 0

    diference_days = fields.Integer(string='Diferença em Dias', compute='_compute_diference_days', store=True)

    def print_packing_slip(self):
        return self.env.ref('print_packing_slip.action_report_packing_slip_template').report_action(self)
