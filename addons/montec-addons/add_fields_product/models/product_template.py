# -*- codding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api

class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    external_of = fields.Float(string="Externo de")
    external_until = fields.Float(string="Externo até")
    internal_of = fields.Float(string="Interno de")
    internal_until = fields.Float(string="Interno até")
    thickness_of = fields.Float(string="Espessura de")
    thickness_until = fields.Float(string="Espessura até")
    height_of = fields.Float(string="Altura de")
    height_until = fields.Float(string="Altura até")
    
    heat_treatment = fields.Char(string="Tratamento Térmico")
    superficial_treatment = fields.Char(string="Tratamento Superficial")
    