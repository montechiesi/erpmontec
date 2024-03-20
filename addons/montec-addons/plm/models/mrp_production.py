from odoo import models, fields, api



class MrpProductionInherit(models.Model):
    _inherit = 'mrp.production'
    
    plm_oae_id = fields.Many2one("plm.oae", "Ordem de Alteração de Engenharia")
    
    @api.model
    def create(self, values):
        res = super(MrpProductionInherit, self).create(values)
        
        for record in res:
            if record.origin or self.env.context.get("sale_order"):
                type_id = self.env['plm.type'].search([('is_auto_order', '=', True)], limit=1).id or 1
                
                start_stage = self.env['plm.stage'].search([('type_ids', 'in', type_id), ('start_stage', '=', True)], limit=1)
                
                if self.env.context.get("sale_order"):
                    orders = self.env.context.get("sale_order").split() 
                else:
                    orders = record.origin.split("-")[-1].replace(" ", "").split(",")
                
                for order in orders:
                    plm_oae_id = self.env['plm.oae'].create({
                        'name': record.product_id.name + " - " + order,
                        'type_id': type_id,
                        'stage_id': start_stage.id if start_stage else None,
                        'product_tmpl_id': record.product_id.product_tmpl_id.id,
                        'qty': record.product_qty,
                        'origin': order,
                        'production_order_id': record.id
                    })
                
                # FIXME: Vai dar ruim
                record.plm_oae_id = plm_oae_id.id
                
                
        
        return res