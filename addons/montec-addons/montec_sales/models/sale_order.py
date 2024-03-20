from odoo import models, fields, api

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    
    has_st = fields.Boolean("Tem S.T?")
    so_number_client = fields.Char("Número do Pedido do Cliente")
    
    shipping_partner = fields.Many2one("res.partner", "Transportadora")