from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class InstallmentWizard(models.TransientModel):
    _name = 'installment.wizard'
    _description = 'Installment Wizard'

    account_move_id = fields.Many2one('account.move', string='Fatura', ondelete='restrict')

    total_installment = fields.Float("Total para Parcelar")
    quantity_installments = fields.Integer("Quantidade de Parcelas")
    value_installments = fields.Float("Valor das Parcelas")
    first_due_date = fields.Date("Vencimento 1a. Parcela", default=datetime.today())
    frequency = fields.Selection([
        ('daily', 'Diário'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensal'),
        ('bimonthly', 'Bimestral'),
        ('quarterly', 'Trimestral'),
        ('four_months', 'Quadrimestral'),
        ('semiannual', 'Semestral'),
        ('yearly', 'Anual'),
        ('every_ten_days', 'A cada 10 dias'),
        ('every_fifthen_days', 'A cada 15 dias'),
        ('every_twenty_eight_days', 'A cada 28 dias')
    ], default="monthly", string="Frequência")

    @api.onchange('quantity_installments')
    def _onchange_value_installments(self):
        if self.quantity_installments > 0:
            self.value_installments = self.total_installment / self.quantity_installments

    # Corrigir o total de cada parcela. Está ficando o mesmo total da fatura original e não os valores da parcela
    def create_installments(self):
        if self.quantity_installments <= 0:
            raise ValidationError("É necessário colocar uma quantidade de parcelas maior que zero.")

        installment_generated = 1
        expiration_date = self.first_due_date
        
        total_quantity_product = 0
        for line in self.account_move_id.invoice_line_ids:
            total_quantity_product += line.quantity
        
        value_product = self.value_installments / total_quantity_product
        invoice_line_ids = []
        for line in self.account_move_id.invoice_line_ids:
            invoice_line_ids.append((0, 0, {
                'name': line.name,
                'quantity': line.quantity,
                'price_unit': value_product,
                'tax_ids': [],
            }))
            
        while installment_generated <= self.quantity_installments:
            invoice = self.env['account.move'].create({
                'partner_id': self.account_move_id.partner_id.id,
                'move_type': self.account_move_id.move_type,
                'amount_total_signed': self.value_installments,
                'amount_total_in_currency_signed': self.value_installments,
                'amount_residual': self.value_installments,
                'installment_value': self.value_installments,
                'invoice_date_due': expiration_date,
                'invoice_line_ids': invoice_line_ids,
            })
            invoice.action_post()
            # copy_account_move = self.account_move_id.copy({
            #     "montec_account_move_id": self.account_move_id.id,
            #     "invoice_payment_term_id": False
            # })
            # copy_account_move.amount_total_signed = self.value_installments
            # copy_account_move.amount_total_in_currency_signed = self.value_installments
            # copy_account_move.amount_residual = self.value_installments
            # copy_account_move.installment_value = self.value_installments
            # copy_account_move.invoice_date_due = expiration_date
            # copy_account_move.action_post()
            if self.frequency == 'daily':                
                expiration_date = expiration_date + relativedelta(days=1)
            elif self.frequency == 'weekly':
                expiration_date = expiration_date + relativedelta(weeks=1)
            elif self.frequency == 'monthly':
                expiration_date = expiration_date + relativedelta(months=1)
            elif self.frequency == 'bimonthly':
                expiration_date = expiration_date + relativedelta(months=2)
            elif self.frequency == 'quarterly':
                expiration_date = expiration_date + relativedelta(months=3)
            elif self.frequency =="four_months":
                expiration_date = expiration_date + relativedelta(months=4)
            elif self.frequency == 'semiannual':
                expiration_date = expiration_date + relativedelta(months=6)
            elif self.frequency == 'yearly':
                expiration_date = expiration_date + relativedelta(years=1)
            elif self.frequency == 'every_ten_days':
                expiration_date = expiration_date + relativedelta(days=10)
            elif self.frequency == 'every_fifthen_days':
                expiration_date = expiration_date + relativedelta(days=15)
            elif self.frequency == "every_twenty_eight_days":
                expiration_date = expiration_date + relativedelta(days=28)
            
            installment_generated += 1

        self.account_move_id.button_cancel()
        return
