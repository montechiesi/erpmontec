# -*- codding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api

class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super(AccountMoveInherit, self).action_post()
        for line in self.line_ids:
            stock_move_id = self.env['stock.move'].search([
                ('sale_line_id', '=', line.sale_line_ids.id),
                ('location_id.usage', '=', 'internal'),
                ('picking_id.state', 'not in', ['done', 'cancel'])
            ])
            stock_move_id.product_uom_qty = line.quantity

        return res
