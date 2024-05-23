from openerp import api, fields, models
from openerp.addons import decimal_precision as dp
from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
from openerp.exceptions import Warning as UserError


class RevisedEstimateXlsxReport(models.TransientModel):
	_name = 'revised.estimate.xlsx.report'

	boq_id = fields.Many2one('bill.of.quantity', string="Name of Work")


	@api.multi
	def generate_xls_report(self):	
		
		return self.env["report"].get_action(self, report_name='custom.revised_estimate_report.xlsx')


class RevisedEstimateReportXlsx(ReportXlsx):
	def generate_xlsx_report(self, workbook, data, invoices):
		worksheet = workbook.add_worksheet("Bill")

		boldc = workbook.add_format({'bold': True,'align': 'center','bg_color':'#D3D3D3'})
		heading_format = workbook.add_format({'bold': True,'align': 'center','size': 10})
		bold = workbook.add_format({'bold': True})
		rightb = workbook.add_format({'align': 'right','bold': True})
		centerb = workbook.add_format({'align': 'center','bold': True})
		bolde = workbook.add_format({'bold': True,'font_color':'brown'})
		right = workbook.add_format({'align': 'right'})
		center = workbook.add_format({'align': 'center'})
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

		row = 4
		col = 0
		new_row = row 
		inv = invoices.boq_id

		worksheet.set_column('B:B', 20)
		worksheet.merge_range('A1:C1', 'Name of work:', boldc)
		worksheet.merge_range('D1:J1', inv.name_of_work.name, boldc)

		worksheet.merge_range('A2:C2', 'Name of Contractor:', boldc)
		worksheet.merge_range('D2:F2', inv.bidder_name.name, boldc)
		
		worksheet.write('G2', 'Agt.No:', boldc)
		worksheet.write('H2', inv.agent_no or '', boldc)
		worksheet.write('I2', 'Date:', boldc)
		worksheet.write('J2', inv.date, boldc)
		
		worksheet.merge_range('A3:J3', 'Revised Estimate',boldc)
		
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
		grand_total = 0.0
		grand_total1 = 0.0
		grand_total2 = 0.0
		amt_tot1 = 0.0
		amt_tot2 = 0.0
		amt_total = 0.0

		for line in inv.line_ids:
			# i+=1
			new_row+=1
			worksheet.write('A%s' %(new_row), line.sl_no)
			worksheet.write('B%s' %(new_row), line.product_id.name)
			qty1 = 0.0
			qty2 = 0.0
			qty_tot1 = 0.0
			qty3 = 0.0
			qty4 = 0.0
			qty_tot2 = 0.0
			qty_total = 0.0
			if line.already_done_ids:
				new_row += 1
				worksheet.write('B%s' %(new_row), 'Already Done', bold)
				#categorise based on item type			
				item_type = []
				for val in line.already_done_ids:
					item_type = item_type+[val.type_id]							
				for d in set(item_type):
					if d.name:
						new_row += 1
						worksheet.write('B%s' %(new_row), d.name, bold)
					for done in line.already_done_ids:	
						qty = "'{%."+str(line.uom_id.decimal_no)+"f}'"
						a = qty % done.qty
						a = a.split('{')[1]
						qty = a.split("}")[0]
						if d.id==done.type_id.id:
							new_row += 1
							worksheet.write('B%s' %(new_row), done.name)
							worksheet.write('C%s' %(new_row), done.no, center)
							worksheet.write('D%s' %(new_row), done.l, center)
							worksheet.write('E%s' %(new_row), done.b, center)
							worksheet.write('F%s' %(new_row), done.d, center)
							worksheet.write('G%s' %(new_row), qty, center)
							qty1 += float(qty)

			if line.already_done_steel_ids:
				new_row += 1
				worksheet.write('B%s' %(new_row), '', bold)

				for steel in line.already_done_steel_ids:	
					qty = "'{%."+str(line.uom_id.decimal_no)+"f}'"
					b = qty % steel.qty
					b = b.split('{')[1]
					qty = a.split("}")[0]
					new_row += 1
					worksheet.write('B%s' %(new_row), steel.name)
					worksheet.write('C%s' %(new_row), steel.no, center)
					worksheet.write('D%s' %(new_row), steel.length, center)
					worksheet.write('E%s' %(new_row), steel.qty_in_meter, center)
					worksheet.write('G%s' %(new_row), qty, center)
					qty2 += float(qty)

			qty_tot1 = qty1 + qty2
			qty = "'{%."+str(line.uom_id.decimal_no)+"f}'"
			t = qty % qty_tot1
			t = t.split('{')[1]
			qty_tot1 = t.split("}")[0]
			if line.already_done_ids or line.already_done_steel_ids:
				new_row += 1
				worksheet.write('B%s' %(new_row), 'Total', bold)
				worksheet.write('G%s' %(new_row), qty_tot1, centerb)
			
			if line.to_be_done_ids:
				new_row += 1
				worksheet.write('B%s' %(new_row), 'To Be Done', bold)
				#categorise based on item type			
				item_type = []
				for val in line.to_be_done_ids:
					item_type = item_type+[val.type_id]							
				for d in set(item_type):
					if d.name:
						new_row += 1
						worksheet.write('B%s' %(new_row), d.name, bold)
					for done in line.to_be_done_ids:
						qty = "'{%."+str(line.uom_id.decimal_no)+"f}'"
						c = qty % done.qty
						c = c.split('{')[1]
						qty = c.split("}")[0]	
						if d.id==done.type_id.id:
							new_row += 1
							worksheet.write('B%s' %(new_row), done.name)
							worksheet.write('C%s' %(new_row), done.no, center)
							worksheet.write('D%s' %(new_row), done.l, center)
							worksheet.write('E%s' %(new_row), done.b, center)
							worksheet.write('F%s' %(new_row), done.d, center)
							worksheet.write('G%s' %(new_row), qty, center)
							qty3 += float(qty)

			if line.to_be_done_steel_ids:
				new_row += 1
				worksheet.write('B%s' %(new_row), '', bold)

				for steel in line.to_be_done_steel_ids:
					qty = "'{%."+str(line.uom_id.decimal_no)+"f}'"
					d = qty % steel.qty
					d = d.split('{')[1]
					qty = d.split("}")[0]	
					new_row += 1
					worksheet.write('B%s' %(new_row), steel.name)
					worksheet.write('C%s' %(new_row), steel.no, center)
					worksheet.write('D%s' %(new_row), steel.length, center)
					worksheet.write('E%s' %(new_row), steel.qty_in_meter, center)
					worksheet.write('G%s' %(new_row), qty, center)
					qty4 += float(qty) 

			qty_tot2 = qty3 + qty4
			qty = "'{%."+str(line.uom_id.decimal_no)+"f}'"
			t = qty % qty_tot2
			t = t.split('{')[1]
			qty_tot2 = t.split("}")[0]
			if line.to_be_done_steel_ids or line.to_be_done_ids:
				new_row += 1
				worksheet.write('B%s' %(new_row), 'Total', bold)
				worksheet.write('G%s' %(new_row), qty_tot2, centerb)
				
			if (not line.already_done_ids) and (not line.already_done_steel_ids) and (not line.to_be_done_ids) and (not line.to_be_done_steel_ids):
				new_row += 1
				worksheet.write('B%s' %(new_row), 'Item not required', bold)
			
			qty_total = float(qty_tot1) + float(qty_tot2)
			qty = "'{%."+str(line.uom_id.decimal_no)+"f}'"
			t = qty % qty_total
			t = t.split('{')[1]
			qty_total = t.split("}")[0]
			new_row += 1
			worksheet.write('B%s' %(new_row), 'Total', bold)
			worksheet.write('G%s' %(new_row), qty_total, centerb)
			worksheet.write('H%s' %(new_row), line.uom_id.name, bold)
			worksheet.write('I%s' %(new_row), "%.2f" % line.estimated_rate, centerb)
			worksheet.write('J%s' %(new_row), "%.2f" % line.untaxed_amt, centerb)
			grand_total1 += float(qty_total)
			amt_tot1 += line.untaxed_amt
		
		# extra line
		extra_row = new_row
		# j=0
		if inv.extra_line_ids:
			extra_row+=1
			worksheet.write('B%s' %(extra_row), 'Extra Items', bolde)

			for line in inv.extra_line_ids:
				# j+=1
				extra_row+=1
				worksheet.write('A%s' %(extra_row), line.sl_no)
				worksheet.write('B%s' %(extra_row), line.product_id.name)
				qty1 = 0.0
				qty2 = 0.0
				qty_tot1 = 0.0
				qty3 = 0.0
				qty4 = 0.0
				qty_tot2 = 0.0
				qty_total = 0.0
				if line.already_done_ids:
					extra_row += 1
					worksheet.write('B%s' %(extra_row), 'Already Done', bold)
					#categorise based on item type			
					item_type = []
					for val in line.already_done_ids:
						item_type = item_type+[val.type_id]							
					for d in set(item_type):
						if d.name:
							extra_row += 1
							worksheet.write('B%s' %(extra_row), d.name, bold)
						for done in line.already_done_ids:
							qty = "'{%."+str(line.uom_id.decimal_no)+"f}'"
							a = qty % done.qty
							a = a.split('{')[1]
							qty = a.split("}")[0]	
							if d.id==done.type_id.id:
								extra_row += 1
								worksheet.write('B%s' %(extra_row), done.name)
								worksheet.write('C%s' %(extra_row), done.no, center)
								worksheet.write('D%s' %(extra_row), done.l, center)
								worksheet.write('E%s' %(extra_row), done.b, center)
								worksheet.write('F%s' %(extra_row), done.d, center)
								worksheet.write('G%s' %(extra_row), qty, center)
								qty1 += float(qty)

				if line.already_done_steel_ids:
					extra_row += 1
					worksheet.write('B%s' %(extra_row), '', bold)

					for steel in line.already_done_steel_ids:
						qty = "'{%."+str(line.uom_id.decimal_no)+"f}'"
						b = qty % steel.qty
						b = b.split('{')[1]
						qty = b.split("}")[0]	
						extra_row += 1
						worksheet.write('B%s' %(extra_row), steel.name)
						worksheet.write('C%s' %(extra_row), steel.no, center)
						worksheet.write('D%s' %(extra_row), "%.2f" % steel.length, center)
						worksheet.write('E%s' %(extra_row), "%.3f" % steel.qty_in_meter, center)
						worksheet.write('G%s' %(extra_row), qty, center)
						qty2 += float(qty)

				qty_tot1 = qty1 + qty2
				qty = "'{%."+str(line.uom_id.decimal_no)+"f}'"
				t = qty % qty_tot1
				t = t.split('{')[1]
				qty_tot1 = t.split("}")[0]
				if line.already_done_ids or line.already_done_steel_ids:
					extra_row += 1
					worksheet.write('B%s' %(extra_row), 'Total', bold)
					worksheet.write('G%s' %(extra_row), qty_tot1, centerb)
			
				if line.to_be_done_ids:
					extra_row += 1
					worksheet.write('B%s' %(extra_row), 'To Be Done', bold)
					#categorise based on item type			
					item_type = []
					for val in line.to_be_done_ids:
						item_type = item_type+[val.type_id]							
					for d in set(item_type):
						if d.name:
							extra_row += 1
							worksheet.write('B%s' %(extra_row), d.name, bold)
						for done in line.to_be_done_ids:
							qty = "'{%."+str(line.uom_id.decimal_no)+"f}'"
							c = qty % done.qty
							c = c.split('{')[1]
							qty = c.split("}")[0]	
							if d.id==done.type_id.id:
								extra_row += 1
								worksheet.write('B%s' %(extra_row), done.name)
								worksheet.write('C%s' %(extra_row), done.no, center)
								worksheet.write('D%s' %(extra_row), done.l, center)
								worksheet.write('E%s' %(extra_row), done.b, center)
								worksheet.write('F%s' %(extra_row), done.d, center)
								worksheet.write('G%s' %(extra_row), qty, center)
								qty3 += float(qty)

				if line.to_be_done_steel_ids:
					extra_row += 1
					worksheet.write('B%s' %(extra_row), '', bold)

					for steel in line.to_be_done_steel_ids:	
						qty = "'{%."+str(line.uom_id.decimal_no)+"f}'"
						d = qty % steel.qty
						d = d.split('{')[1]
						qty = d.split("}")[0]
						extra_row += 1
						worksheet.write('B%s' %(extra_row), steel.name)
						worksheet.write('C%s' %(extra_row), steel.no, center)
						worksheet.write('D%s' %(extra_row), "%.2f" % steel.length, center)
						worksheet.write('E%s' %(extra_row), "%.3f" % steel.qty_in_meter, center)
						worksheet.write('G%s' %(extra_row), qty, center)
						qty4 += float(qty) 

				qty_tot2 = qty3 + qty4
				qty = "'{%."+str(line.uom_id.decimal_no)+"f}'"
				t = qty % qty_tot2
				t = t.split('{')[1]
				qty_tot2 = t.split("}")[0]
				if line.to_be_done_ids or line.to_be_done_steel_ids:
					extra_row += 1
					worksheet.write('B%s' %(extra_row), 'Total', bold)
					worksheet.write('G%s' %(extra_row), qty_tot2, centerb)
			
				qty_total = float(qty_tot1) + float(qty_tot2)
				qty = "'{%."+str(line.uom_id.decimal_no)+"f}'"
				t = qty % qty_total
				t = t.split('{')[1]
				qty_total = t.split("}")[0]
				extra_row += 1
				worksheet.write('B%s' %(extra_row), 'Total', bold)
				worksheet.write('G%s' %(extra_row), qty_total, centerb)
				worksheet.write('H%s' %(extra_row), line.uom_id.name, bold)
				worksheet.write('I%s' %(extra_row), "%.2f" % line.extra_rate, centerb)
				worksheet.write('J%s' %(extra_row), "%.2f" % line.untaxed_amt, centerb)
				grand_total2 += float(qty_total)
				amt_tot2 += line.untaxed_amt
		total_row = extra_row + 1
		grand_total = grand_total1 + grand_total2
		
		amt_total = amt_tot1 + amt_tot2
		worksheet.write('B%s' %(total_row), 'Grand Total', bold)
		worksheet.write('G%s' %(total_row), "%.3f" % grand_total, centerb)
		worksheet.write('J%s' %(total_row), "%.2f" % amt_total, centerb)



RevisedEstimateReportXlsx('report.custom.revised_estimate_report.xlsx','revised.estimate.xlsx.report')