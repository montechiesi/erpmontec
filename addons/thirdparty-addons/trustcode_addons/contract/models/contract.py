# Copyright 2004-2010 OpenERP SA
# Copyright 2014 Angel Moya <angel.moya@domatix.com>
# Copyright 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016-2018 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError,UserError
from odoo.tools.translate import _


class ContractContract(models.Model):
    _name = 'contract.contract'
    _description = "Contract"
    _order = 'code, name asc'
    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
        'contract.abstract.contract',
    ]

    active = fields.Boolean(default=True,)
    code = fields.Char(
        string="Reference",
    )
    invoice_to_parent_company = fields.Boolean(string="Faturar para Matriz")
    parent_partner_id = fields.Many2one(
        string="Empresa Matriz",
        comodel_name='res.partner',
        ondelete='restrict',
    )

    contract_template_id = fields.Many2one(
        string='Contract Template', comodel_name='contract.template'
    )
    contract_line_ids = fields.One2many(
        string='Contract lines',
        comodel_name='contract.line',
        inverse_name='contract_id',
        copy=True,
    )

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        index=True,
        default=lambda self: self.env.user,
    )
    create_invoice_visibility = fields.Boolean(
        compute='_compute_create_invoice_visibility'
    )
    recurring_next_date = fields.Date(
        compute='_compute_recurring_next_date',
        string='Date of Next Invoice',
        store=True,
    )
    date_end = fields.Date(
        compute='_compute_date_end', string='Date End', store=True
    )
    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term', string='Payment Terms', index=True
    )
    payment_journal_id = fields.Many2one(
        'account.journal', string='Forma de pagamento')
    invoice_count = fields.Integer(compute="_compute_invoice_count")
    fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string='Fiscal Position',
        ondelete='restrict',
    )
    invoice_partner_id = fields.Many2one(
        string="Invoicing contact",
        comodel_name='res.partner',
        ondelete='restrict',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        inverse='_inverse_partner_id',
        required=True
    )

    commercial_partner_id = fields.Many2one(
        'res.partner',
        related='partner_id.commercial_partner_id',
        store=True,
        string='Commercial Entity',
        index=True
    )

    amount_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)

    def _inverse_partner_id(self):
        for rec in self:
            if not rec.invoice_partner_id:
                rec.invoice_partner_id = rec.partner_id.address_get(
                    ['invoice']
                )['invoice']

    def _get_related_invoices(self):
        self.ensure_one()
        invoices = (
            self.env['account.move'].search([('contract_id','=',self.id),]) )
        return invoices

    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = len(rec._get_related_invoices())

    def action_show_invoices(self):
        self.ensure_one()
        tree_view_ref = (
            'account.move_supplier_tree' if self.contract_type == 'purchase' else 'account.move_tree_with_onboarding'
        )
        form_view_ref = (
            'account.move_supplier_form' if self.contract_type == 'purchase' else 'account.move_form'
        )
        tree_view = self.env.ref(tree_view_ref, raise_if_not_found=False)
        form_view = self.env.ref(form_view_ref, raise_if_not_found=False)
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'view_type': 'form',
            'view_mode': 'tree,form,activity',
            'domain': [('id', 'in', self._get_related_invoices().ids)],
        }
        if tree_view and form_view:
            action['views'] = [(tree_view.id, 'tree'), (form_view.id, 'form')]
        return action

    @api.depends('contract_line_ids.price_total', 'contract_line_ids.is_canceled')
    def _compute_amount(self):
        for line in self:
            line.amount_total = sum(x.price_total for x in line.contract_line_ids if not x.is_canceled)

    @api.depends('contract_line_ids.date_end')
    def _compute_date_end(self):
        for contract in self:
            contract.date_end = False
            date_end = contract.contract_line_ids.mapped('date_end')
            if date_end and all(date_end):
                contract.date_end = max(date_end)

    @api.depends(
        'contract_line_ids.recurring_next_date',
        'contract_line_ids.is_canceled',
    )
    def _compute_recurring_next_date(self):
        for contract in self:
            recurring_next_date = contract.contract_line_ids.filtered(
                lambda l: l.recurring_next_date and not l.is_canceled
            ).mapped('recurring_next_date')
            if recurring_next_date:
                contract.recurring_next_date = min(recurring_next_date)
            else:
                contract.recurring_next_date = False 
                
    @api.depends('contract_line_ids.create_invoice_visibility')
    def _compute_create_invoice_visibility(self):
        for contract in self:
            contract.create_invoice_visibility = any(
                contract.contract_line_ids.mapped(
                    'create_invoice_visibility'
                )
            )

    @api.onchange('contract_template_id')
    def _onchange_contract_template_id(self):
        """Update the contract fields with that of the template.

        Take special consideration with the `contract_line_ids`,
        which must be created using the data from the contract lines. Cascade
        deletion ensures that any errant lines that are created are also
        deleted.
        """
        contract_template_id = self.contract_template_id
        if not contract_template_id:
            return
        lines_dict = []
        for field_name, field in contract_template_id._fields.items():
            if field.name == 'contract_line_ids':
                for template_line in contract_template_id.contract_line_ids:
                    line = {}
                    for line_field_name, field in template_line._fields.items():
                        if line_field_name!='contract_id'  and not any((field.compute, field.related, field.automatic, field.readonly,field.company_dependent)):
                            line[line_field_name] = template_line[line_field_name]
                    line['create_invoice_visibility'] = False
                    line['date_start'] = self.date
                    line['recurring_next_date'] = self.date
                    lines_dict += [line]
            elif not any(
                (
                    field.compute,
                    field.related,
                    field.automatic,
                    field.readonly,
                    field.company_dependent,
                    field.name in self.NO_SYNC,
                )):
                if self.contract_template_id[field_name]:
                    self[field_name] = self.contract_template_id[field_name]
        if lines_dict:
            self.contract_line_ids = [(5,0,0)]+[(0,0,x) for x in lines_dict]


    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.pricelist_id = self.partner_id.property_product_pricelist.id
        self.fiscal_position_id = self.partner_id.property_account_position_id
        if self.contract_type == 'purchase':
            self.payment_term_id = \
                self.partner_id.property_supplier_payment_term_id
        else:
            self.payment_term_id = \
                self.partner_id.property_payment_term_id
        self.invoice_partner_id = self.partner_id.address_get(['invoice'])[
            'invoice'
        ]
        return {
            'domain': {
                'invoice_partner_id': [
                    '|',
                    ('id', 'parent_of', self.partner_id.id),
                    ('id', 'child_of', self.partner_id.id),
                ]
            }
        }

    def _prepare_invoice(self, date_invoice, journal=None):
        """
        Taken from sale/models/sale.py
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        if self.contract_type == 'sale':
            invoice_type = 'out_invoice'
        else: #purchase
            invoice_type = 'in_invoice'
        if not journal:
            if self.journal_id:
                journal = self.journal_id
            else:
                journal = self.env['account.move'].with_context(force_company=self.company_id.id, default_type=invoice_type)._get_default_journal()
                if not journal:
                    raise UserError(_('Please define an accounting %s journal for the company %s (%s).') % (self.contract_type, self.company_id.name, self.company_id.id))

        currency = (
            self.pricelist_id.currency_id
            or self.partner_id.property_product_pricelist.currency_id
            or self.company_id.currency_id
        )

        invoice_vals = {
            'name' : '/',
            'invoice_date': date_invoice,
            'date': date_invoice,
            'auto_post':self.auto_post,
            'move_type': invoice_type,
            'journal_id': journal.id,
            'invoice_origin': '%s - %s' % (self.name or '', self.code or ''),
            'company_id': self.company_id.id,
            'currency_id': currency.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            'partner_id': self.parent_partner_id.id or self.invoice_partner_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.parent_partner_id.property_account_position_id.id or self.invoice_partner_id.property_account_position_id.id,
            'invoice_incoterm_id': self.incoterm_id.id, 
            'invoice_payment_term_id': self.payment_term_id.id,
            'payment_journal_id': self.payment_journal_id.id,
            'invoice_line_ids': [],
            'user_id': self.user_id.id,
            'contract_id': self.id,
        }
        return invoice_vals


    def action_contract_send(self):
        self.ensure_one()
        template = self.env.ref('contract.email_contract_template', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form')
        ctx = dict(
            default_model='contract.contract',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    @api.model
    def _finalize_invoice_values(self, invoice_values):
        """
        This method adds the missing values in the invoice lines dictionaries.

        If no account on the product, the invoice lines account is
        taken from the invoice's journal in _onchange_product_id
        This code is not in finalize_creation_from_contract because it's
        not possible to create an invoice line with no account

        :param invoice_values: dictionary (invoice values)
        :return: updated dictionary (invoice values)
        """
        # If no account on the product, the invoice lines account is
        # taken from the invoice's journal in _onchange_product_id
        # This code is not in finalize_creation_from_contract because it's
        # not possible to create an invoice line with no account
        new_invoice = self.env['account.move'].new(invoice_values)

      
        for invoice_line in new_invoice.invoice_line_ids:
            name = invoice_line.name
            analytic_account_id = invoice_line.analytic_account_id
            price_unit = invoice_line.price_unit
            invoice_line.invoice_id = new_invoice
            invoice_line._onchange_product_id()
            invoice_line.update(
                {
                     'name': name,
                     'analytic_account_id': analytic_account_id,
                     'price_unit': price_unit,
                })
        return new_invoice._convert_to_write(new_invoice._cache)


    @api.model
    def _finalize_and_create_invoices(self, invoices_values):
        """
        This method:
         - finalizes the invoices values (onchange's...)
         - creates the invoices
         - finalizes the created invoices (onchange's, tax computation...)
        :param invoices_values: list of dictionaries (invoices values)
        :return: created invoices (account.move)
        """
        if isinstance(invoices_values, dict):
            invoices_values = [invoices_values]
        final_invoices_values = []
        for invoice_values in invoices_values:
            final_invoices_values.append(
                self._finalize_invoice_values(invoice_values)
            )
        invoices = self.env['account.move'].create(final_invoices_values)
        return invoices

    @api.model
    def _get_contracts_to_invoice_domain(self, date_ref=None):
        """
        This method builds the domain to use to find all
        contracts (contract.contract) to invoice.
        :param date_ref: optional reference date to use instead of today
        :return: list (domain) usable on contract.contract
        """
        domain = []
        if not date_ref:
            date_ref = fields.Date.context_today(self)
        domain.extend([('recurring_next_date', '<=', date_ref)])
        return domain

    def _get_lines_to_invoice(self, date_ref):
        """
        This method fetches and returns the lines to invoice on the contract
        (self), based on the given date.
        :param date_ref: date used as reference date to find lines to invoice
        :return: contract lines (contract.line recordset)
        """
        self.ensure_one()
        return self.contract_line_ids.filtered(
            lambda l: not l.is_canceled
            and l.recurring_next_date
            and l.recurring_next_date <= date_ref
        )

    def _prepare_recurring_invoices_values(self, date_ref=False):
        """
        This method builds the list of invoices values to create, based on
        the lines to invoice of the contracts in self.
        !!! The date of next invoice (recurring_next_date) is updated here !!!
        :return: list of dictionaries (invoices values)
        """
        invoices_values = []
        for contract in self:
            if not date_ref:
                date_ref = contract.recurring_next_date
            if not date_ref:
                # this use case is possible when recurring_create_invoice is
                # called for a finished contract
                continue
            contract_lines = contract._get_lines_to_invoice(date_ref)
            if not contract_lines:
                continue
            invoice_values = contract._prepare_invoice(date_ref)
            for line in contract_lines:
                invoice_values.setdefault('invoice_line_ids', [])
                invoice_line_values = line._prepare_invoice_line() # function in contact_line
                if invoice_line_values:
                    invoice_values['invoice_line_ids'].append(
                        (0, 0, invoice_line_values)
                    )
            invoices_values.append(invoice_values)
            contract_lines._update_recurring_next_date()
        return invoices_values

    def recurring_create_invoice(self):
        """
        This method triggers the creation of the next invoices of the contracts
        even if their next invoicing date is in the future.
        """
        return self._recurring_create_invoice()

    def _recurring_create_invoice(self, date_ref=False):
        invoices_values = self._prepare_recurring_invoices_values(date_ref)
        invoices = self.env['account.move'].create(invoices_values)
        return invoices

    @api.model
    def cron_recurring_create_invoice(self):
        domain = self._get_contracts_to_invoice_domain()
        contracts_to_invoice = self.search(domain)
        date_ref = fields.Date.context_today(contracts_to_invoice)
        contracts_to_invoice._recurring_create_invoice(date_ref)
