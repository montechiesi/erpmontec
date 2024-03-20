# -*- codding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api

class StockWarehouseOrderpointInherit(models.Model):
    _inherit = "stock.warehouse.orderpoint"
    
    @api.model
    def create(self, vals):
        res = super(StockWarehouseOrderpointInherit, self).create(vals)
        res.trigger = 'auto'
        res.action_replenish_auto()
        #res.action_open_orderpoints()
        return res
    
    
    
    # compute_trigger = fields.Boolean(compute='_compute_compute_trigger', string='compute_trigger')

    # def _compute_compute_trigger(self):
    #     for record in self:
    #         if record.compute_trigger:
    #             record.action_replenish_auto()
    #             record.action_open_orderpoints()
    #             record.compute_trigger = True
    
    
        

class MrpProductionInherit(models.Model):
    _inherit = 'mrp.production'

    sale_order_line_id = fields.Many2one('sale.order.line', string="Linha do Pedido de Vendas")
    nominal_one = fields.Float(string="Nominal Externo")
    nominal_two = fields.Float(string="Nominal Interno")
    nominal_three = fields.Float(string="Nominal Espessura")
    material_sae = fields.Float(string="Material SAE")

    @api.model
    def create(self, values):
        res = super(MrpProductionInherit, self).create(values)
        if res.origin or self.env.context.get("sale_order"):
            if self.env.context.get("sale_order"):
                sale_name = self.env.context.get("sale_order").split()
            else:
                sale_name =  res.origin.split('- ')
            
            if sale_name:
                sale_order_id = self.env['sale.order'].search([('name', '=', sale_name[-1])])
                if sale_order_id:
                    sale_order_line_id = self.env['sale.order.line'].search([('order_id', '=', sale_order_id.id), ('product_id', '=', res.product_id.id)])
                    if sale_order_line_id:
                        res.sale_order_line_id = sale_order_line_id.id
        return res

    def print_report(self):
        # order_line_ids = list(map(lambda x: x.id, self.order_line))

        data = {
            'object': self.read([])[0],
            'production_ids': self.ids,
        }

        report_name = 'sale_production_order.action_order_production_template'
        report_action = self.env.ref(report_name).report_action(self, data=data)

        report_action.update({'print_report_name': f'Ordens de Produção - {self.name}'})

        return report_action
