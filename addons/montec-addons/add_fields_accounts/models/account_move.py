# -*- codding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    carrier = fields.Char(string="Portador")
    observation = fields.Text(string="Observação")
    competence = fields.Date(string="Competência", default=fields.Date.context_today)
    code_pix = fields.Char(string="Cod. de barras/pix")
    
    document_number = fields.Char(string="Número documento")
    frequency = fields.Selection([
        ('daily', 'Diário'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensal'),
        ('bimonthly', 'Bimestral'),
        ('quarterly', 'Trimestral'),
        ('semiannual', 'Semestral'),
        ('yearly', 'Anual'),
        ('every_ten_days', 'A cada 10 dias'),
        ('every_fifthen_days', 'A cada 15 dias ')
    ], string="Frequência")
    
    last_emission_date = fields.Date(string="Data da Última emissão")
    next_emission_date = fields.Date(string="Data da Última emissão")

    state = fields.Selection(
        selection_add=[('invoice_model', 'Modelo')],
        ondelete={'invoice_model': 'set default'},
    )
    
    @api.model
    def _get_invoice_in_payment_state(self):
        return 'paid'
    
    def confirm_invoice_frequency(self):
        self.state = 'invoice_model'

    def montec_create_account(self):
        hoje = datetime.now().date()
        accounts = self.search([('state', '=', 'invoice_model'), ('frequency', '!=', False)])
        for account in accounts:
            if account.frequency == 'daily':                
                new_account = account.copy()
                new_account.frequency = ''
                diference = 0
                if account.invoice_date_due and account.invoice_date:
                    diference = (account.invoice_date_due - account.invoice_date).days
                new_account.invoice_date = hoje
                new_account.invoice_date_due = hoje + timedelta(days=diference)
                account.last_emission_date = hoje
                account.next_emission_date = hoje + timedelta(days=1)
            elif account.frequency == 'weekly':
                if not account.next_emission_date or account.next_emission_date == hoje:
                    new_account = account.copy()
                    new_account.frequency = ''
                    diference = 0
                    if account.invoice_date_due and account.invoice_date:
                        diference = (account.invoice_date_due - account.invoice_date).days
                    new_account.invoice_date = hoje
                    new_account.invoice_date_due = hoje + timedelta(days=diference)    
                    account.last_emission_date = hoje
                    account.next_emission_date = hoje + timedelta(days=7)
                        
            elif account.frequency == 'monthly':
                if not account.next_emission_date or account.next_emission_date == hoje:
                    new_account = account.copy()
                    new_account.frequency = ''
                    diference = 0
                    if account.invoice_date_due and account.invoice_date:
                        diference = (account.invoice_date_due - account.invoice_date).days
                    new_account.invoice_date = hoje
                    new_account.invoice_date_due = hoje + timedelta(days=diference)    
                    account.last_emission_date = hoje
                    account.next_emission_date = hoje + relativedelta(months=1)
                    
            elif account.frequency == 'bimonthly':
                if not account.next_emission_date or account.next_emission_date == hoje:
                    new_account = account.copy()
                    new_account.frequency = ''
                    diference = 0
                    if account.invoice_date_due and account.invoice_date:
                        diference = (account.invoice_date_due - account.invoice_date).days
                    new_account.invoice_date = hoje
                    new_account.invoice_date_due = hoje + timedelta(days=diference)    
                    account.last_emission_date = hoje
                    account.next_emission_date = hoje + relativedelta(months=2)

            elif account.frequency == 'quarterly':
                if not account.next_emission_date or account.next_emission_date == hoje:
                    new_account = account.copy()
                    new_account.frequency = ''
                    diference = 0
                    if account.invoice_date_due and account.invoice_date:
                        diference = (account.invoice_date_due - account.invoice_date).days
                    new_account.invoice_date = hoje
                    new_account.invoice_date_due = hoje + timedelta(days=diference)    
                    account.last_emission_date = hoje
                    account.next_emission_date = hoje + relativedelta(months=3)

            elif account.frequency == 'semiannual':
                if not account.next_emission_date or account.next_emission_date == hoje:
                    new_account = account.copy()
                    new_account.frequency = ''
                    diference = 0
                    if account.invoice_date_due and account.invoice_date:
                        diference = (account.invoice_date_due - account.invoice_date).days
                    new_account.invoice_date = hoje
                    new_account.invoice_date_due = hoje + timedelta(days=diference)    
                    account.last_emission_date = hoje
                    account.next_emission_date = hoje + relativedelta(months=6)

            elif account.frequency == 'yearly':
                if not account.next_emission_date or account.next_emission_date == hoje:
                    new_account = account.copy()
                    new_account.frequency = ''
                    diference = 0
                    if account.invoice_date_due and account.invoice_date:
                        diference = (account.invoice_date_due - account.invoice_date).days
                    new_account.invoice_date = hoje
                    new_account.invoice_date_due = hoje + timedelta(days=diference)    
                    account.last_emission_date = hoje
                    account.next_emission_date = hoje + relativedelta(year=1)

            elif account.frequency == 'every_ten_days':
                if not account.next_emission_date or account.next_emission_date == hoje:
                    new_account = account.copy()
                    new_account.frequency = ''
                    diference = 0
                    if account.invoice_date_due and account.invoice_date:
                        diference = (account.invoice_date_due - account.invoice_date).days
                    new_account.invoice_date = hoje
                    new_account.invoice_date_due = hoje + timedelta(days=diference)    
                    account.last_emission_date = hoje
                    account.next_emission_date = hoje + timedelta(days=10)

            elif account.frequency == 'every_fifthen_days':
                if not account.next_emission_date or account.next_emission_date == hoje:
                    new_account = account.copy()
                    new_account.frequency = ''
                    diference = 0
                    if account.invoice_date_due and account.invoice_date:
                        diference = (account.invoice_date_due - account.invoice_date).days
                    new_account.invoice_date = hoje
                    new_account.invoice_date_due = hoje + timedelta(days=diference)    
                    account.last_emission_date = hoje
                    account.next_emission_date = hoje + timedelta(days=15)
