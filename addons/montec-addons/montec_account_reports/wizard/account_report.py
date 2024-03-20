# models.py
from odoo import models, fields, api
from xlsxwriter.workbook import Workbook

import base64
import io

class ReportWizard(models.TransientModel):
    _name = 'report.wizard'
    _description = 'Report Wizard'

    
    report_type = fields.Selection([
        ('cash_flow', 'Fluxo de Caixa'),
        ('dre', 'Demonstração do resultado do exercício'),
        ('best_seller', 'Melhor Vendedor'),
    ], string='Tipo de Relatório', required=True)
    start_date = fields.Date('Data Inicial', required=False)
    end_date = fields.Date('Data Final', required=False)
    account_analytical_id = fields.Many2one("account.analytic.account", "Conta Analítica")
    journal_id = fields.Many2one("account.journal", "Diário")
    #posteds = fields.Boolean("Somente Movimentos Lançados", default=True)


    def _get_mounth(self, day):
        
        mounth = {
            '01': "JANEIRO",
            "02": "FEVEREIRO",
            "03": "MARÇO",
            "04": "ABRIL",
            "05": "MAIO",
            "06": "JUNHO",
            "07": "JULHO",
            "08": "AGOSTO",
            "09": "SETEMBRO",
            "10": "OUTUBRO",
            "11": "NOVEMBRO",
            "12": "DEZEMBRO"
        }
        
        return mounth.get(day[3:5])

    def cash_flow_report(self, dados, saldo_entrada=0, saldo_saida=0 ):
        # Crie o arquivo XLSX
        output = io.BytesIO()
        workbook = Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        title_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 14,
            'bg_color': '#000000',
            'font_color': '#FFFFFF'
        })
        
        subtitle_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 14,
            'bg_color': '#FFFF00',
            'font_color': '#000000'
        })

        worksheet.merge_range('B2:E5', 'FLUXO DE CAIXA MENSAL', title_format)

        row = 5
        mes_atual = False
     

        saldo = saldo_entrada + saldo_saida
        for day, move in list(dados.items()):
            
            if self._get_mounth(day) != mes_atual:
                worksheet.write(row, 2, saldo_saida)
                worksheet.write(row, 3, saldo_entrada)
                worksheet.write(row, 4, saldo)
                
                row += 3
                worksheet.merge_range(f'B{row}:E{row+2}', self._get_mounth(day), subtitle_format)
                mes_atual = self._get_mounth(day)
                row += 3
                worksheet.write(row, 1, "Data")
                worksheet.write(row, 2, "Saídas")
                worksheet.write(row, 3, "Entradas")
                worksheet.write(row, 4, "Saldo")
                row += 1
                
            worksheet.write(row, 1, day)
            worksheet.write(row, 2, move["amount_total"] if move["move_type"] == "in_invoice" else 0.0)
            worksheet.write(row, 3, move["amount_total"] if move["move_type"] == "out_invoice" else 0.0)
            
            if move["move_type"] == "out_invoice":
                saldo_entrada += move["amount_total"]
                saldo += move["amount_total"]
            else:
                saldo_saida -= move["amount_total"]
                saldo -= move["amount_total"] 
            
            worksheet.write(row, 4, saldo)
            row += 1

        worksheet.write(row, 2, saldo_saida)
        worksheet.write(row, 3, saldo_entrada)
        worksheet.write(row, 4, saldo)
        
        workbook.close()
        # Retorne o relatório em formato binário
        report_data = output.getvalue()
        output.close()

        return report_data

    def dre_report(self, dados_agrupados ):
        
        # Crie o arquivo XLSX
        output = io.BytesIO()
        workbook = Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        title_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 14,
            'bg_color': '#000000',
            'font_color': '#FFFFFF'
        })
        
        subtitle_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 14,
            'bg_color': '#FFFF00',
            'font_color': '#000000'
        })

        worksheet.merge_range('A1:F5', 'Demonstração do resultado do exercício', title_format)
        worksheet.merge_range('A6:B6', '', title_format)
        worksheet.merge_range('C6:F6', '', title_format)
             
        row = 7
        for key, value in list(dados_agrupados.items()):
            tot_section = 0.0
            worksheet.merge_range(f'A{row+1}:B{row+1}', key, subtitle_format)
            tot_section_line = row+1
            row += 1
            
            tots_perc_line_rows = []
            for ky, vl in list(value.items()):
                line_tot = sum([ move.balance for move in vl ])
                worksheet.merge_range(f'A{row+1}:B{row+1}', ky)
                worksheet.merge_range(f'C{row+1}:F{row+1}', line_tot)
                tot_section += line_tot
                tots_perc_line_rows.append((row, line_tot))
                row += 1
               
               
            worksheet.merge_range(f'C{tot_section_line}:F{tot_section_line}', tot_section, subtitle_format)
            
            for row_line, line_tot in tots_perc_line_rows:
                if tot_section > 0:
                    worksheet.write(row_line, 6, str(round(line_tot * 100 / tot_section, 2)) + "%")
                else:
                    worksheet.write(row_line, 6, "0.0%")
            
        workbook.close()
        # Retorne o relatório em formato binário
        report_data = output.getvalue()
        output.close()

        return report_data
    
    def best_seller_report(self, dados):
        # Crie o arquivo XLSX
        output = io.BytesIO()
        workbook = Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet()

        row = 0
        for name, total in dados:
            worksheet.write(row, 0, name)
            worksheet.write(row, 1, total)
            row += 1


        
        workbook.close()
        # Retorne o relatório em formato binário
        report_data = output.getvalue()
        output.close()

        return report_data
        
    def _group_by_date(self, moves):
        
        dados = {}
        for move in moves:
            
            date_string = move.invoice_date.strftime('%d/%m/%Y') if move.invoice_date else move.create_date.strftime('%d/%m/%Y')
            if move.move_type == "out_invvoice":
            
                if not dados.get(date_string):
                    
                    dados[date_string] = {
                        "amount_total": move.amount_total,
                        "move_type": move.move_type,
                    }
                else:
                    dados[date_string]["amount_total"] += move.amount_total
                
            else:
                if not dados.get(date_string):
                    
                    dados[date_string] = {
                        "amount_total": move.amount_total,
                        "move_type": move.move_type,
                    }
                else:
                    dados[date_string]["amount_total"] -= move.amount_total
                    
        return dados

    def _tratar_dados_dre(self, moves):
    
        dados_agrupados = {}
        for move in moves:
            
            if not dados_agrupados.get(move.account_id.user_type_id.name):
                dados_agrupados[move.account_id.user_type_id.name] = {}
            
            if not dados_agrupados[move.account_id.user_type_id.name].get(move.account_id.name):
                dados_agrupados[move.account_id.user_type_id.name][move.account_id.name] = []
            
            dados_agrupados[move.account_id.user_type_id.name][move.account_id.name].append(move)
                
        return dados_agrupados
                
    def print_report(self):
        
        order = 'invoice_date ASC'
        filtros = []
        if self.start_date:
            filtros.append(('create_date', '>=', self.start_date))
        
        if self.end_date:
            filtros.append(('create_date', '<=', self.end_date))
        
        if self.account_analytical_id:
            filtros.append(('analytical_account', '=', self.account_analytical_id.id))
            
        if self.journal_id:
            filtros.append(('journal_id', '=', self.journal_id.id))
            
        
        if self.report_type == 'cash_flow':
            saldo_entrada = saldo_saida = 0
            if self.start_date:
                faturas_saida  = self.env['account.move'].search([('create_date', '<', self.start_date), ('move_type', '=', 'out_invoice')], order=order)
                saldo_entrada = sum([saida.amount_total for saida in faturas_saida])
                
                faturas_entrada  = self.env['account.move'].search([('create_date', '<', self.start_date), ('move_type', '=', 'in_invoice')], order=order)
                saldo_saida = sum([entrada.amount_total for entrada in faturas_entrada])
                
            moves = self.env["account.move"].search(filtros, order=order)
            dados = self._group_by_date(moves)
            report_data = self.cash_flow_report(dados, saldo_entrada, saldo_saida)
            report_name = 'Fluxo de Caixa.xlsx'
        elif self.report_type == 'dre':
            move_lines = self.env["account.move.line"].search(filtros)
            dados_agrupados = self._tratar_dados_dre(move_lines)
            report_data = self.dre_report( dados_agrupados )
            report_name = 'DRE.xlsx'
            
        elif self.report_type == 'best_seller':
            
            # Execute uma consulta SQL
            query = """
                select rp.name, sum(am.amount_total) as total from account_move as am
                inner join res_users as ru
                on ru.id = am.invoice_user_id
                inner join res_partner as rp
                on rp.id = ru.partner_id
                group by rp.name,ru.id, am.invoice_user_id
                order by total
            """
            self.env.cr.execute(query)

            # Obtenha os resultados da consulta
            registros = self.env.cr.fetchall()
            
            report_data = self.best_seller_report( registros )
            report_name = 'best_seller.xlsx'
        

        # Crie o anexo do relatório
        attachment = self.env['ir.attachment'].create({
            'name': report_name,
            'type': 'binary',
            'datas': base64.b64encode(report_data),
            'store_fname': report_name,
            'res_model': self._name,
            'res_id': self.id,
        })

        # Abra a visualização do anexo
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s/%s' % (attachment.id, report_name),
            'target': 'self',
        }