from odoo import models, fields, api

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    
    plm_stage_products = fields.Text(compute='_compute_plm_stage_products', string='Estágio de Produção')
    
    def _compute_plm_stage_products(self):
        
        for order in self:
            stages = ""
            for line in order.order_line:
                if line.plm_stage_products:
                    stages += "<br/>" + line.plm_stage_products
                
            order.plm_stage_products = stages
            

class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'
    
    plm_stage_products = fields.Text(compute='_compute_plm_stage_products', string='Estágio de Produção')
    
    def _compute_plm_stage_products(self):
        for line in self:
            oae_ids = self.env["plm.oae"].search([('product_tmpl_id', '=', line.product_id.product_tmpl_id.id), ('origin', '=', line.order_id.name)])
            stages = ""
            for oae in oae_ids:
                stages += "<br/>" + oae.name or "" + " - " + oae.stage_id.name or ""
                
            line.plm_stage_products = stages
        
    
    
