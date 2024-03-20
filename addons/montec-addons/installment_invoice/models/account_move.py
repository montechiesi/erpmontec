# -*- codding: utf-8 -*-
from odoo import models, fields, api

class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    montec_account_move_id = fields.Many2one('account.move', string='Fatura Total', ondelete='restrict')
    montec_account_move_ids = fields.One2many('account.move', 'montec_account_move_id', string='Parcelas')
    installment_value = fields.Float(string='Valor da Parcela')

    analytical_account = fields.Many2one("account.analytic.account", "Conta Analítica")

    state = fields.Selection(
        selection_add=[('installment', 'Parcelamento')],
        ondelete={'installment': 'set default'},
    )

    def pay_in_installments(self):
        wizard = self.env['installment.wizard'].create({
            "account_move_id": self.id,
            "total_installment": self.amount_residual
        })

        return {
            'name': 'Report Wizard Title',
            'type': 'ir.actions.act_window',
            'res_model': 'installment.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('installment_invoice.view_installment_wizard_form').id,
            'res_id': wizard.id,
            'target': 'new',
        }


    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.balance',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id',
        'state')
    def _compute_amount(self):
        super(AccountMoveInherit, self)._compute_amount()
        
        for move in self:
            if move.installment_value and move.installment_value > 0:
                move.amount_total_signed = move.installment_value
                move.amount_total_in_currency_signed = move.installment_value
                move.amount_residual = move.installment_value
                move.tax_totals_json = move.installment_value
