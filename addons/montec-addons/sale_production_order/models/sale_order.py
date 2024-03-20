from odoo import models, fields, api


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    
    def action_confirm(self):
        res = super(SaleOrderInherit, self).action_confirm()
        for record in self:
            record.env["stock.warehouse.orderpoint"].with_context(sale_order=record.name).action_open_orderpoints()
            
        return res