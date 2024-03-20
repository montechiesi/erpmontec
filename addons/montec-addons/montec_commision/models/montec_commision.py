from odoo import models, fields, api


class MontecComission(models.Model):
    _name = 'montec.commission'
    _description = "Módulo de comissões"
    _rec_name = 'salesman'
    
    
    salesman = fields.Many2one("res.users", "Vendedor")
    
    commission_percentage = fields.Float("Percentual de Comissão")
    
    commission_value = fields.Float("Valor de Comissão")
    
    
    