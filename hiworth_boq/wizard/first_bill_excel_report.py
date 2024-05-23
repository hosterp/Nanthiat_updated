from openerp import api, fields, models
from openerp.addons import decimal_precision as dp
from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
from openerp.exceptions import Warning as UserError



class FirstBillXlsxReport1(models.TransientModel):
	_name = 'first.bill.xlsx.report1'

	invoice_no = fields.Many2one('account.invoice',string="Invoice Number", domain="[('is_first_bill', '=', True)]")


	@api.multi
	def generate_xls_report(self):	
		
		return self.env["report"].get_action(self, report_name='custom.first_bill_report.xlsx')




class BillReportXlsx(ReportXlsx):
	def generate_xlsx_report(self, workbook, data, invoices):
		worksheet = workbook.add_worksheet("Bill")
		# raise UserError(str(invoices.invoice_no.id))

		boldc = workbook.add_format({'bold': True,'align': 'center','bg_color':'#D3D3D3'})
		heading_format = workbook.add_format({'bold': True,'align': 'center','size': 10})
		bold = workbook.add_format({'bold': True})
		rightb = workbook.add_format({'align': 'right','bold': True})
		right = workbook.add_format({'align': 'right'})
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
		# formater = workbook.add_format({'border':1})
		# worksheet.set_column('A0:A7',15,formater)
		# worsheet.set_margins({left:0.7, right:0.7, top:0.75, bottom:0.75})


		row = 3
		col = 0
		new_row = row 
		inv = invoices.invoice_no
		worksheet.set_column('B:B', 20)
		worksheet.merge_range('A1:C1', 'Name of work:', boldc)
		worksheet.merge_range('D1:J1', inv.project_id.name, boldc)

		worksheet.merge_range('A2:C2', 'Name of Contractor:', boldc)
		worksheet.merge_range('D2:F2', inv.boq_ref_id.bidder_name.name, boldc)
		
		worksheet.write('G2', 'Agt.No:', boldc)
		worksheet.write('H2', inv.boq_ref_id.agent_no or '', boldc)
		worksheet.write('I2', 'Date:', boldc)
		worksheet.write('J2', inv.date_invoice or '', boldc)
		
		worksheet.write('A%s' %(row), 'Sl No.', boldc)
		worksheet.write('B%s' %(row), 'Description', boldc)
		worksheet.write('C%s' %(row), 'No.', boldc)
		worksheet.write('D%s' %(row), 'L', boldc)
		worksheet.write('E%s' %(row), 'B', boldc)
		worksheet.write('F%s' %(row), 'D', boldc)
		worksheet.write('G%s' %(row), 'Qty', boldc)
		worksheet.write('H%s' %(row), 'Unit', boldc)
		worksheet.write('I%s' %(row), 'Rate', boldc)
		worksheet.write('J%s' %(row), 'Amount', boldc)

		# i = 0
		qty = 0.0
		qty1 = 0.0
		qty2 = 0.0
		for line in inv.invoice_line:
			# i+=1
			new_row+=1
			worksheet.write('A%s' %(new_row), line.sl_no)
			worksheet.write('B%s' %(new_row), line.product_id.name)
			
			boq_row = new_row
			
			for boq in line.boq_ids:
				boq_row+=1
				qty = "'{%."+str(line.uos_id.decimal_no)+"f}'"
				a = qty % boq.qty
				a = a.split('{')[1]
				a = a.split("}")[0]


				worksheet.write('B%s' %(boq_row), boq.name)
				worksheet.write('C%s' %(boq_row), boq.no, right)
				worksheet.write('D%s' %(boq_row), boq.l, right)
				worksheet.write('E%s' %(boq_row), boq.b, right)
				worksheet.write('F%s' %(boq_row), boq.d, right)
				worksheet.write('G%s' %(boq_row), a, right)
				qty1 += float(a) 

			steel_row = boq_row
			for steel in line.steel_ids:
				steel_row+=1
				qty = "'{%."+str(line.uos_id.decimal_no)+"f}'"
				b = qty % steel.qty
				b = b.split('{')[1]
				b = b.split("}")[0]				

				worksheet.write('B%s' %(steel_row), steel.name)
				worksheet.write('C%s' %(steel_row), steel.no, right)
				worksheet.write('D%s' %(steel_row), steel.length, right)
				worksheet.write('E%s' %(steel_row), steel.qty_in_meter, right)
				worksheet.write('G%s' %(steel_row), b, right)
				qty2 += float(b)	
			qty_tot = qty1+qty2		
			total_row = steel_row+1
			worksheet.write('B%s' %(total_row), 'Total', bold)
			worksheet.write('G%s' %(total_row), qty_tot, rightb)
			worksheet.write('H%s' %(total_row), line.uos_id.name, bold)
			worksheet.write('I%s' %(total_row), line.price_unit, rightb)
			worksheet.write('J%s' %(total_row), line.price_subtotal, rightb)



BillReportXlsx('report.custom.first_bill_report.xlsx','first.bill.xlsx.report1')