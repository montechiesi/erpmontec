from odoo import models, fields, api, SUPERUSER_ID

    
class ProductLifeCycleManagementOAE(models.Model):
    _name = 'plm.oae'
    _inherit = ['mail.thread']
    
    name = fields.Char("Descrição", tracking=True, required=True)
    type_id = fields.Many2one('plm.type', "Tipo", tracking=True, required=True)
    stage_id = fields.Many2one('plm.stage', "Estágio", tracking=True, group_expand='_read_group_stage_ids')
    origin = fields.Char("Origem")
    sale_order_id = fields.Many2one("sale.order", "Pedido de Venda")
    partner_sale = fields.Many2one(related='sale_order_id.partner_id', string="Cliente")
    qty = fields.Char("Quantidade")
    production_order_id = fields.Many2one("mrp.production", "Ordem de Produção")
    
    @api.model
    def _read_group_stage_ids(self, stage_id, domain, order):
        search_domain = [('type_ids', 'in', self.env.context['active_id'])]
        stage_ids = stage_id._search(search_domain, order='order', access_rights_uid=SUPERUSER_ID)
        return stage_id.browse(stage_ids)
    
    
    product_tmpl_id = fields.Many2one('product.template', "Produto", tracking=True, required=True)
    user_id = fields.Many2one('res.users', string="Responsável", tracking=True)
    tag_ids = fields.Many2many('plm.tag', string='Marcadores', tracking=True)
    note = fields.Text("Nota", tracking=True)
    plm_oae_approval_ids = fields.One2many('plm.oae.approval.lines', 'plm_oae_id', string='Aprovações')
    
    @api.model
    def create(self, vals):
        # Obter a próxima sequência
        sequence_value = self.env['ir.sequence'].next_by_code('plm.oea.seq')
        if sequence_value and vals['name']:
            vals['name'] = sequence_value + " " + vals['name']
            
        res = super(ProductLifeCycleManagementOAE, self).create(vals)
        
        if res.origin:
            sale_order_id = self.env["sale.order"].search([('name', '=', res.origin)])
            if sale_order_id:
                res.sale_order_id = sale_order_id.id
            
        
        return res
    
    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        for record in self:
            if record.stage_id.final_stage:
                mrp_inter = self.env["mrp.immediate.production"].browse(record.production_order_id.id)
                if mrp_inter:
                    mrp_inter.process()
    
class ProductLifeCycleManagementApprovalLinesOAE(models.Model):
    _name = 'plm.oae.approval.lines'
    
    name = fields.Char("Função")
    plm_oae_id = fields.Many2one('plm.oae', string='Ordem de alteração de engenharia')
    user_id = fields.Many2one('res.users', string='Aprovado por')
    state = fields.Selection([
        ('none', 'Ainda não'),
        ('comment', 'Comentário'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
    ], string='Status')
    approval_date = fields.Datetime("Data de Aprovação")
    stage_id = fields.Many2one("plm.stage", "Estágio da aprovação")
    required_user_ids = fields.Many2many("res.users", string="Usuários solicitados")
    
class ProductLifeCycleManagementType(models.Model):
    _name = 'plm.type'
    
    name = fields.Char("Nome")
    alias_name = fields.Char("Alias de e-mail")
    nb_ecos = fields.Integer("Número de ordens", compute="_compute_nb_ecos")
    color = fields.Char("Cor")
    is_auto_order = fields.Boolean("Gerar Ordens Automaticamente")
    
    def _compute_nb_ecos(self):
        for record in self:
            orders = self.env["plm.oae"].search([('type_id', '=', record.id)])
            if orders:
                record.nb_ecos = len(orders)
            else:
                record.nb_ecos = 0
    
    
class ProductLifeCycleManagementStage(models.Model):
    _name = 'plm.stage'
    
    name = fields.Char('Nome')
    type_ids = type_ids = fields.Many2many('plm.type', string='Tipos')
    order = fields.Integer(string="Ordem")
    final_stage = fields.Boolean("Estágio final")
    start_stage = fields.Boolean("Estágio inicial")
    approval_line_ids = fields.One2many('plm.stage.approval.lines', 'plm_stage_id', string='Aprovações')
    description = fields.Text("Descrição")
    
    @api.onchange('start_stage')
    def _onchange_start_stage(self):
        self.order = 0
        
    def create(self, vals):
        vals["type_ids"] = [(6, 0, self.env.context.get("active_ids") )]
        res = super(ProductLifeCycleManagementStage, self).create(vals)
        return res
    
class ProductLifeCycleManagementStageApprovalLines(models.Model):
    _name = 'plm.stage.approval.lines'
    
    name = fields.Char("Função")
    plm_stage_id = fields.Many2one('plm.stage', string='Estágio Ordem de Engenharia')
    user_ids = fields.Many2many('res.users', string='Usuários')
    approval_type = fields.Selection([
        ('optional', 'Aprova, mas a aprovação é opcional'),
        ('mandatory', 'É necessário aprovar'),
        ('comment', 'Somente comentários'),
    ], string='Tipo de Aprovação')
    
class ProductLifeCycleManagementTag(models.Model):
    _name = 'plm.tag'
    
    name = fields.Char("Nome")