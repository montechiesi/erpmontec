from odoo import models, fields, api


class MontecComissionReportWizard(models.TransientModel):
    _name = "montec.comission.report.wizard"
    _description = "Wizard com filtro para relatório"

    date_from = fields.Date("Data de")

    date_to = fields.Date("Data até")

    salesman = fields.Many2one("res.users", "Vendedor")

    def print_report(self):
        self.ensure_one()
        [data] = self.read()

        domain = [
            ("invoice_date_due", ">=", self.date_from),
            ("invoice_date_due", "<=", self.date_to),
            (
                "invoice_user_id",
                "=",
                self.salesman.id,
            ),  # Ou qualquer outro estado de fatura que você deseja pesquisar
        ]

        invoices = self.env["account.move"].search(domain)
        if invoices:
            domain = [
                ("salesman", "=", self.salesman.id),
            ]

            comissao = self.env["montec.commission"].search(domain)
            if comissao:
                data["emp"] = invoices.ids

                dados = [
                    {
                        "vendedor": invoice.invoice_user_id.name,
                        "valor": invoice.amount_total,
                        "comissao": comissao[0].commission_value
                        or (
                            comissao[0].commission_percentage
                            * invoice.amount_total
                            / 100
                        ),
                        "fatura": invoice.name,
                        "data": invoice.create_date,
                    }
                    for invoice in invoices
                ]

                datas = {
                    "ids": invoices.ids,
                    "dados": dados,
                    "model": "montec.commission",
                    "form": data,
                }
                return self.env.ref(
                    "montec_commision.montec_commission_action_report"
                ).report_action(docids=invoices, data=datas)
