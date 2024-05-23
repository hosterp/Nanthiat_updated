from openerp import api, fields, models
from openerp.addons import decimal_precision as dp
from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
from openerp.exceptions import Warning as UserError



class ComparativeStatementXlsxReport(models.TransientModel):
	_name = 'comparative.statement.xlsx.report'

	boq_id = fields.Many2one('bill.of.quantity',string="Work of Name")


	@api.multi
	def generate_xls_report(self):	
		
		return self.env["report"].get_action(self, report_name='custom.comparative_statement_report.xlsx')


class ComparativeStatementReportXlsx(ReportXlsx):
	def generate_xlsx_report(self, workbook, data, invoices):
		worksheet = workbook.add_worksheet("CS")

		boldc = workbook.add_format({'bold': True,'align': 'center'})
		heading_format = workbook.add_format({'bold': True,'align': 'center','size': 10})
		bold = workbook.add_format({'bold': True})
		rightb = workbook.add_format({'align': 'right','bold': True})
		centerb = workbook.add_format({'align': 'center','bold': True})
		center = workbook.add_format({'align': 'center'})
		right = workbook.add_format({'align': 'right'})
		bolde = workbook.add_format({'bold': True,'font_color':'brown'})
		merge_format = workbook.add_format({
		'bold': 1,
		'border': 1,
		'align': 'center',
		'valign': 'vcenter',
		'bg_color': '#D3D3D3',
		'font_color': '#000000',
		})
		format_hidden = workbook.add_format({
		'hidden': True
		})
		align_format = workbook.add_format({
		'align': 'right',
		})

		row = 7
		col = 0
		new_row = row 
		inv = invoices.boq_id
		worksheet.set_column('B:B', 20)
		worksheet.set_row('2', boldc)

		worksheet.merge_range('A1:Q1', inv.tender_inviting_authority, boldc)

		worksheet.write('A2', 'Package No.:', boldc)
		worksheet.write('B2', inv.package_no or '', boldc)
		worksheet.write('C2', 'Name of Work:', boldc)
		worksheet.merge_range('D2:K2', inv.name_of_work.name or '', boldc)
		worksheet.write('L2', 'Block:', boldc)
		worksheet.write('M2',inv.block_id.name or '', boldc)
		worksheet.write('N2', 'Panchayath:', boldc)
		worksheet.write('O2', inv.panchayath_id.name or '', boldc)
		worksheet.write('P2', 'District:', boldc)
		worksheet.write('Q2', inv.district_id.name or '', boldc)
		
		worksheet.merge_range('A3:Q3', 'Comparative Statement', boldc)

		worksheet.merge_range('A4:A7', 'Sl No.', boldc)
		worksheet.merge_range('B4:B7', 'Description', boldc)
		worksheet.merge_range('C4:E4', 'Original Quantity', boldc)
		worksheet.merge_range('F4:L4', 'Revised Estimate', boldc)
		worksheet.merge_range('M4:M7', 'Savings(Minus) in Rs', boldc)
		worksheet.merge_range('N4:N7', 'Excess(Plus) in Rs', boldc)
		worksheet.merge_range('O4:O7', 'Explanation', boldc)
		worksheet.merge_range('P4:P7', 'Remarks of KSRRDA', boldc)
		worksheet.merge_range('Q4:Q7', 'Remarks of SE', boldc)

		
		worksheet.merge_range('C5:C7', 'Quantity', boldc)
		worksheet.merge_range('D5:D7', 'Rate(Rs/Ps)', boldc)
		worksheet.merge_range('E5:E7', 'Amount(Rs)', boldc)
		
		worksheet.merge_range('F5:H5', 'Quantity', boldc)
		worksheet.merge_range('I5:I7', 'Rate', boldc)
		worksheet.merge_range('J5:L5', 'Amount of Work', boldc)

		# worksheet.merge_range('J6:L6', 'Amount of Work', boldc)

		worksheet.write('F7', 'Already Executed', boldc)
		worksheet.write('G7', 'To Be Executed', boldc)
		worksheet.write('H7', 'Total', boldc)

		worksheet.write('J7', 'Already Executed', boldc)
		worksheet.write('K7', 'To Be Executed', boldc)
		worksheet.write('L7', 'Total', boldc)
		

		for line in inv.line_ids:
			new_row+=1

			qty = "'{%."+str(line.uom_id.decimal_no)+"f}'"
			a = qty % line.already_executed_qty
			a = a.split('{')[1]
			already_executed_qty = a.split("}")[0]
			
			b = qty % line.to_be_executed_qty
			b = b.split('{')[1]
			to_be_executed_qty = b.split("}")[0]

			c = qty % line.total_quantity
			c = c.split('{')[1]
			total_quantity = c.split("}")[0]


			worksheet.write('A%s' %(new_row), line.sl_no)
			worksheet.write('B%s' %(new_row), line.product_id.name)
			worksheet.write('C%s' %(new_row), line.quantity,center)
			worksheet.write('D%s' %(new_row), line.estimated_rate,center)
			worksheet.write('E%s' %(new_row), line.untaxed_amt,center)
			worksheet.write('F%s' %(new_row), already_executed_qty,center)
			worksheet.write('G%s' %(new_row), to_be_executed_qty,center)
			worksheet.write('H%s' %(new_row), total_quantity,center)
			worksheet.write('I%s' %(new_row), line.revised_rate,center)
			worksheet.write('J%s' %(new_row), "%.2f" % line.already_executed_revised,center)
			worksheet.write('K%s' %(new_row), "%.2f" % line.to_be_executed_revised,center)
			worksheet.write('L%s' %(new_row), "%.2f" % line.revised_total,center)
			worksheet.write('M%s' %(new_row), line.savings,center)
			worksheet.write('N%s' %(new_row), line.excess,center)
			worksheet.write('O%s' %(new_row), line.explanation or '', center)
			worksheet.write('P%s' %(new_row), line.remarks_ksrrda or '', center)
			worksheet.write('Q%s' %(new_row), line.remarks_se or '', center)
		
		extra_row = new_row
		if inv.extra_line_ids:
			extra_row+=1
			worksheet.write('B%s' %(extra_row), 'Extra Items', bolde)

			for line in inv.extra_line_ids:
				extra_row+=1

				qty = "'{%."+str(line.uom_id.decimal_no)+"f}'"
				a = qty % line.already_executed_qty
				a = a.split('{')[1]
				already_executed_qty = a.split("}")[0]
				
				b = qty % line.to_be_executed_qty
				b = b.split('{')[1]
				to_be_executed_qty = b.split("}")[0]

				c = qty % line.total_quantity
				c = c.split('{')[1]
				total_quantity = c.split("}")[0]

				worksheet.write('A%s' %(extra_row), line.sl_no)
				worksheet.write('B%s' %(extra_row), line.product_id.name)
				worksheet.write('C%s' %(extra_row), line.quantity, center)
				worksheet.write('D%s' %(extra_row), line.estimated_rate, center)
				worksheet.write('E%s' %(extra_row), line.untaxed_amt, center)
				worksheet.write('F%s' %(extra_row), line.already_executed_qty, center)
				worksheet.write('G%s' %(extra_row), line.to_be_executed_qty, center)
				worksheet.write('H%s' %(extra_row), line.total_quantity, center)
				worksheet.write('I%s' %(extra_row), line.revised_rate, center)
				worksheet.write('J%s' %(extra_row), "%.2f" % line.already_executed_revised, center)
				worksheet.write('K%s' %(extra_row), "%.2f" % line.to_be_executed_revised, center)
				worksheet.write('L%s' %(extra_row), "%.2f" % line.revised_total, center)
				worksheet.write('M%s' %(extra_row), line.savings, center)
				worksheet.write('N%s' %(extra_row), line.excess, center)
				worksheet.write('O%s' %(extra_row), line.explanation or '', center)
				worksheet.write('P%s' %(extra_row), line.remarks_ksrrda or '', center)
				worksheet.write('Q%s' %(extra_row), line.remarks_se or '', center)
				

ComparativeStatementReportXlsx('report.custom.comparative_statement_report.xlsx','comparative.statement.xlsx.report')