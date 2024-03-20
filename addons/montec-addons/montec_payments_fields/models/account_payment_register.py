from odoo import models, fields, api

class AccountPaymentRegisterInherit(models.TransientModel):
    _inherit = 'account.payment.register'
        
    multa = fields.Monetary(currency_field='currency_id', store=True, string='Multa')
    juros = fields.Monetary(currency_field='currency_id', store=True, string='Juros')
    
    @api.depends('can_edit_wizard', 'source_amount', 'source_amount_currency', 'source_currency_id', 'company_id', 'currency_id', 'payment_date', 'multa', 'juros')
    def _compute_amount(self):
        res = super(AccountPaymentRegisterInherit, self)._compute_amount()
        for wizard in self:
            if wizard.source_currency_id and wizard.can_edit_wizard:
                wizard.amount = wizard.amount + wizard.multa + wizard.juros
            else:
                # The wizard is not editable so no partial payment allowed and then, 'amount' is not used.
                wizard.amount = None
        return
