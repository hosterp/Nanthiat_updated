from openerp import fields, models, api
import datetime
from openerp.exceptions import Warning as UserError
from openerp.osv import osv
from openerp.tools.translate import _
from dateutil import relativedelta
from openerp.exceptions import except_orm, ValidationError

class PaymentsPayments(models.Model):

	_name = 'payments.payments'

	approval_id = fields.Many2one('payment.approvals.line')
	statement_id = fields.Many2one('partner.daily.statement')
	payment_type_id = fields.Many2one('payment.approvals.type', 'Type')
	purchase_boolean = fields.Boolean('Purchase Bill')
	bill = fields.Many2one('purchase.order', 'Bills')
	account_id = fields.Many2one('account.account', 'Account', related="approval_id.account_id")
	project_id = fields.Many2one('project.project', 'Related Project', related="approval_id.project_id")
	amount = fields.Float('Amount')
	amount_approved = fields.Float('Approved Amount', related="approval_id.amount_approved")
	narration = fields.Char('Narration')
	state = fields.Selection([('req', 'Requested'), ('pra', 'Partially Approved'), ('dn', 'Done')], default='req')

	@api.model
	def create(self, vals):
		res = super(PaymentsPayments, self).create(vals)
		print vals
		approvals = self.env['payment.approvals'].search([('date', '=', datetime.datetime.now().date())])
		if approvals:
			line_id = self.env['payment.approvals.line'].create({
				'approval_id': approvals.id or False,
				'type': self.type.id or False,
				'bill': self.bill.id or False,
				'account_id': self.account_id or False,
				'project_id': self.project_id or False,
				'amount': self.amount or False,
				'amount_approved': self.amount_approved or False,
				'narration': self.narration or False,
				'state': self.state or False,
			})
			print ")_)_)_+_+_+_", line_id
			# self.approval_id = line_id.id
		else:
			approval = self.env['payment.approvals'].create({'date': datetime.datetime.now().date()})
			line_id = self.env['payment.approvals.line'].create({
				'approval_id': approval.id or False,
				'type': self.payment_type_id.id or False,
				'bill': self.bill.id or False,
				'account_id': self.account_id.id or False,
				'project_id': self.project_id.id or False,
				'amount': self.amount or False,
				'amount_approved': self.amount_approved or False,
				'narration': self.narration or False,
				'state': self.state or False,
			})
			print "-*--*-*-*--*", line_id
			# self.approval_id = line_id.id
		return res


class PaymentApprovalsType(models.Model):

	_name = 'payment.approvals.type'

	name = fields.Char("Name")



class PartnerDailyStatement(models.Model):
	_name = 'partner.daily.statement'
	_order = 'date desc'


	@api.onchange('date','location_ids')
	def onchange_date_location(self):
		# print 'test========================'
		if self.date and self.location_ids:
			if self.state == 'draft':
				rec = self.env['reception.temporary'].sudo().search([('date','=',self.date),('to_id','=',self.location_ids.id)])
				# print 'recc=======================', rec
				if rec:
					line_ids = []
					for line in rec:
						# print 'sssssssss=================', line.total,line.start_km
						values = {
							'from_id2':line.from_id2.id,
							'item_expense2':line.item_expense2.id,
							'qty':line.qty,
							'rate':line.rate,
							'total':line.total,
							'voucher_no':line.voucher_no,
							'contractor_id':line.contractor_id,
							'rent':line.rent,
							'start_km':line.start_km,
							'end_km':line.end_km,
							'total_km':line.total_km,
							'vehicle_id':line.vehicle_id.id,
							'remarks':line.remarks,
							'driver_stmt_id':line.driver_stmt_id,
							'status': 'new',
							'purchase_id': line.purchase_id.id,
							'invoice_date': line.invoice_date
						}
						line_ids.append((0, False, values ))
					self.received_ids = line_ids


	@api.multi
	@api.depends('rent_vehicle_stmts')
	def get_rent_vehicle_amount(self):
		advance = 0
		for line in self.rent_vehicle_stmts:
			advance += line.advance
		self.rent_vehicle = advance

	
	@api.multi
	def get_category(self):
		for rec in self:
			cat_str=''
			for cate in rec.attendance_ids:
				total = 0
				for line in cate.line_ids:
					total += line.total
			

				cat_str += cate.category_id.name + ': ' + str(total) + '  '
			pur_str =''
			total_pur = 0
			for pur in rec.purchase_ids:
				total_pur += pur.amount_total
				pur_str += pur.name + ': ' + str(total_pur) + '  '
			
			return cat_str + pur_str 





	@api.multi
	def request_approve(self):
		view_ref = self.env['ir.model.data'].get_object_reference('hiworth_construction', 'view_request_approve_line')
		view_id = view_ref[1] if view_ref else False
		res = {
			'type': 'ir.actions.act_window',
			'name': _('Add Approvers'),
			'res_model': 'approver.lines',
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': view_id,
			'target': 'new',
			'context': {'default_name':self.id}
		}

		return res


	@api.multi
	@api.depends('pre_balance','receipts')
	def compute_total(self):
		for rec in self:
			rec.total = rec.pre_balance+rec.receipts


	@api.multi
	@api.depends('total','expense','transfer_amount')
	def compute_balance(self):
		for rec in self:
			rec.balance = rec.total-rec.expense -rec.transfer_amount
			rec.theoretical_balance = rec.balance - rec.get_transferred_amount1()[0] + rec.compute_received_amount1()[0]

	@api.multi
	@api.depends('expense_line_ids','operator_daily_stmts','rent_vehicle_stmts','purchase_ids')
	def compute_expense(self):
		for rec in self:
			expense = 0
			expense2 = 0
			operator_expense = 0
			operator_advance = 0
			rent_vehicle = 0
			labour_expense = 0
			for rent_lines in rec.rent_vehicle_stmts:
				rent_vehicle += rent_lines.advance
			# print "rent_vehiclepartner..................",rec.rent_vehicle
			for lines in rec.purchase_ids:
				expense += lines.amount_total
			for exp_lines in rec.expense_line_ids:
				print 'exp_lines.total--------------------///////', exp_lines.total
				expense2 += exp_lines.total
			if rec.operator_daily_stmts:
				for exp in rec.operator_daily_stmts:
					operator_expense += exp.expense
					operator_advance += exp.advance
			if rec.attendance_ids:
				for attend in rec.attendance_ids:
					for labour in attend.line_ids:
						labour_expense += labour.total
			rec.expense = expense + expense2 + operator_expense + operator_advance + rent_vehicle + labour_expense
	# @api.depends('line_ids','payment_line')
	# def compute_expense(self):
	# 	for rec in self:
	# 		expense = 0
	# 		for lines in rec.line_ids:
	# 			expense += lines.payment_total
	# 		for line in rec.payment_line:
	# 			expense += line.amount
	# 		rec.expense = expense 

	@api.one
	def get_transferred_amount1(self):
		records = self.env['cash.confirm.transfer'].sudo().search([('state','=','accepted'),('date','=',self.date),('name','=',self.employee_id.id)])
		amount = 0
		if records:
			for line in records:
				amount += line.amount
		return amount

	@api.one
	def compute_received_amount1(self):
		rec = self.env['cash.confirm.transfer'].search([('state','=','accepted'),('date','=',self.date),('user_id','=',self.employee_id.id)])
		received = 0
		if rec:
			for line in rec:
				received += line.amount
		return received

	@api.one
	def get_transferred_amount(self):
		records = self.env['cash.confirm.transfer'].sudo().search([('date','=',self.date),('name','=',self.employee_id.id)])
		amount = 0
		if records:
			for line in records:
				amount += line.amount
		self.transfer_amount = amount

	@api.one
	def compute_received_amount(self):
		rec = self.env['cash.confirm.transfer'].search([('date','=',self.date),('user_id','=',self.employee_id.id)])
		received = 0
		if rec:
			for line in rec:
				received += line.amount
		self.receipts = received

	@api.model
	def default_get(self, default_fields):
		vals = super(PartnerDailyStatement, self).default_get(default_fields)
		user = self.env['res.users'].search([('id','=',self.env.user.id)])

		# statement = self.env['partner.daily.statement'].search([('state','=','draft'),('employee_id','=',user.employee_id.id)])
		# if statement:
		# 	raise osv.except_osv(_('Error!'),_("You have old statement to confirm."))

		if user:
			if user.employee_id:
				vals.update({'employee_id' : user.employee_id.id,
							 'pre_balance':user.employee_id.petty_cash_account.balance,
							 'account_id': user.employee_id.petty_cash_account.id,
							 })
			if not user.employee_id and user.id != 1:
				raise osv.except_osv(_('Error!'),_("User and Employee is not linked."))

		return vals

	#need to change
	# @api.one
	# def get_manpower_ids(self):
	# 	self.material_ids.unlink()
	# 	self.manpower_ids.unlink()
	# 	category = []
	# 	work = []		

	# 	labour = self.env['labour.attendance'].search([('attendance_id','=',self.id)])
	# 	labour1 = self.env['labour.attendance'].search([('attendance_id','=',self.id)], limit=1)

	# 	other = self.env['group.attendance'].search([('group_id','=',self.id)])
	# 	line = self.env['labour.attendance.line'].search([('line_id','=',labour1.id)])
	# 	for categ in labour:
	# 		if categ.category_id.id not in category:
	# 			category.append(categ.category_id.id)
	# 	print '|||||||||||||||||||||||||',category

	# 	for wrk in line:
	# 		if wrk.item_of_work.id not in work:
	# 			work.append(wrk.item_of_work.id)

	# 	for val in other:
	# 		if val.category_id.id not in category:
	# 			category.append(val.category_id.id)
	# 		if val.item_of_work.id not in work:
	# 			work.append(val.item_of_work.id)

	# 	vals = []
	# 	for c in category:
	# 		for w in work:
	# 			x = 0
	# 			theoritical = 0
	# 			labour = self.env['labour.attendance.line'].search([('attendance','=',True),('line_id.attendance_id','=',self.id),('line_id.category_id','=',c),('item_of_work','=',w)])
	# 			contract = self.env['group.attendance'].search([('group_id','=',self.id),('category_id','=',c),('item_of_work','=',w)])
	# 			# manpower = self.env['manpower.estimation'].search([('estimate_id','=',self.estimate_id.id),('work_id','=',w),('category_id','=',c)])
	# 			unit = self.env['product.uom'].search([('name','=','Nos')])
	# 			# for val in manpower:
	# 			# 	theoritical += val.qty
	# 			x = x + len(labour) + contract.count	

	# 			if x > 0:			

	# 				vals.append((0, 0,{
	# 							'manpower_id':self.id,
	# 							'item_of_work':w,
	# 							'category_id':c,
	# 							# 'theoritical_qty':theoritical,
	# 							'actual_qty':x,
	# 							'unit':unit.id,
	# 						}))

	# 	materials = []

	# 	master = self.env['todays.work.details'].search([('todays_id','=',self.id)])
	# 	for temp in master:
	# 		categ = self.env['task.category'].search([('name','=','Labour')])
	# 		resource = self.env['todays.work.resources'].search([('resource_line_id','=',temp.id),('categ_id','!=',categ.id)])
	# 		for val in resource:
	# 			materials.append((0, 0,{
	# 							'material_id':self.id,
	# 							'item_id':val.resource_id.id,
	# 							'item_of_work':temp.name.id,
	# 							# 'theoritical_qty':c,
	# 							'actual_qty':val.tot_qty,
	# 							'unit':val.uom_id.id,
	# 						}))

	# 	print vals,"_+_+_+_+_+_+_+_+_+_"
	# 	self.manpower_ids = vals	
	# 	self.material_ids = materials

	# new_one
	@api.one
	def get_consumption(self):
		self.item_usage_lines.unlink()
		self.manpower_ids.unlink()
		category = []
		work = []

		labour = self.env['labour.attendance'].search([('attendance_id','=',self.id)])
		labour1 = self.env['labour.attendance'].search([('attendance_id','=',self.id)], limit=1)

		other = self.env['group.attendance'].search([('group_id','=',self.id)])
		line = self.env['labour.attendance.line'].search([('line_id','=',labour1.id)])
		for categ in labour:
			if categ.category_id.id not in category:
				category.append(categ.category_id.id)

		for wrk in line:
			if wrk.item_of_work.id not in work:
				work.append(wrk.item_of_work.id)

		for val in other:
			if val.category_id.id not in category:
				category.append(val.category_id.id)
			if val.item_of_work.id not in work:
				work.append(val.item_of_work.id)

		vals = []
		for c in category:
			for w in work:
				x = 0
				# theoritical = 0
				labour = self.env['labour.attendance.line'].search([('attendance','=',True),('line_id.attendance_id','=',self.id),('line_id.category_id','=',c),('item_of_work','=',w)])
				contract = self.env['group.attendance'].search([('group_id','=',self.id),('category_id','=',c),('item_of_work','=',w)])
				# manpower = self.env['manpower.estimation'].search([('estimate_id','=',self.estimate_id.id),('work_id','=',w),('category_id','=',c)])
				unit = self.env['product.uom'].search([('name','=','Nos')])
				categ = self.env['labour.category'].search([('id','=',c)])
				# for val in manpower:
				# 	theoritical += val.qty
				x = x + len(labour) + contract.count

				if x > 0:

					vals.append((0, 0,{
						'manpower_id':self.id,
						'item_of_work':w,
						'category_id':c,
						'pricelist_id':categ.pricelist_id.id,
						# 'theoritical_qty':theoritical,
						'actual_qty':x,
						'unit':unit.id,
					}))

		materials = []

		master = self.env['todays.work.details'].search([('todays_id','=',self.id)])
		for temp in master:
			categ = self.env['task.category'].search([('name','=','Labour')])
			resource = self.env['todays.work.resources'].search([('resource_line_id','=',temp.id),('categ_id','!=',categ.id)])
			for val in resource:
				site = self.env['stock.move'].search([('location_dest_id','=',self.location_ids.id),('product_id.product_categ','=',val.resource_id.id)],limit=1)
				materials.append((0, 0,{
					'report_id':self.id,
					'product_categ':val.resource_id.id,
					'product_id':site.product_id.id,
					'item_of_work':temp.name.id,
					'uom_id':val.uom_id.id,
					'receipts':val.tot_qty,
					# 'actual_qty':val.tot_qty,
				}))

		self.manpower_ids = vals
		self.item_usage_lines = materials



	name = fields.Char('Name')
	date = fields.Date('Date', default=datetime.date.today())
	employee_id = fields.Many2one('hr.employee', 'Supervisor')
	reviewer_id = fields.Many2one('res.users', string='Reviewer')
	validator_id = fields.Many2one('res.users', string='Validator')
	account_id = fields.Many2one('account.account', 'Account')
	location_ids = fields.Many2one('stock.location', 'Site', domain=[('usage','=','internal')])
	line_ids = fields.One2many('partner.daily.statement.line', 'report_id', 'Lines', domain=[('expense','!=',True)])
	expense_line_ids = fields.One2many('partner.daily.statement.line', 'report_id', 'Lines', domain=[('expense','=',True)])
	pre_balance = fields.Float('Pre. Balance')
	receipts = fields.Float('Receipts', compute='compute_received_amount')
	total = fields.Float(compute='compute_total', string='Total')
	expense = fields.Float(compute='compute_expense', string='Expense')
	transfer_amount = fields.Float('Transferred Amount',compute="get_transferred_amount")
	balance = fields.Float(compute='compute_balance', string='Actual Balance')
	item_usage_lines = fields.One2many('item.usage', 'report_id', 'Materials Used')
	work_details = fields.Text('Details Of Work Done At Site',required=False)
	tmrw_work_arrangement = fields.Text(required=False)
	details_rqrd_item = fields.One2many('site.purchase','site_id')
	state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('approved','Approved'),('checked','Checked'),('cancelled','Cancelled')],default='draft')
	received_ids = fields.One2many('daily.statement.item.received', 'received_id', 'Receptions')
	next_approver = fields.Many2one('res.users','Next Approver',readonly=True)
	approvers  = fields.One2many('supervisor.statement.approvers','approver_id',readonly=True)
	theoretical_balance = fields.Float('Theoretical Balance', compute="compute_balance")
	reception = fields.Boolean(default=False,compute="get_reception_trenafer")
	transfer = fields.Boolean(default=False,compute="get_reception_trenafer")
	rent_vehicle = fields.Float('Rent Vehicle',compute="get_rent_vehicle_amount")
	approved_by = fields.Many2one('res.users','Approved By')
	approved_sign = fields.Binary('Sign')
	checked_by = fields.Many2one('res.users','Checked By')
	checked_sign = fields.Binary('Sign')
	rent_vehicle_stmts = fields.One2many('rent.vehicle.statement','rent_id')
	operator_daily_stmts = fields.One2many('operator.daily.statement','operator_id')
	machinery_fuel_collection = fields.One2many('machinery.fuel.collection','collection_id')
	machinery_fuel_allocation = fields.One2many('machinery.fuel.allocation','allocation_id')
	payment_line = fields.One2many('pay.labour','labour_id')
	product_ids = fields.One2many('partner.statement.products','line_id', compute="_get_product_ids", store=True)
	fuel_transfer_ids = fields.One2many('partner.fuel.transfer','transfer_id')
	project_id = fields.Many2one('project.project',string="Project")
	# today_work_ids = fields.One2many('today.work','today_work_id')
	tomrw_work_ids = fields.One2many('today.work','tomrw_work_id')
	material_ids = fields.One2many('material.consumption','material_id')
	manpower_ids = fields.One2many('manpower.consumption','manpower_id')
	attendance_ids = fields.One2many('labour.attendance', 'attendance_id')

	group_ids = fields.One2many('group.attendance', 'group_id')
	other_ids = fields.One2many('other.attendance', 'other_id')

	payment_ids = fields.One2many('payments.payments', 'statement_id')
	# others_ids = fields.One2many('other.attendance', 'others_id')
	sub_contarctor_ids=fields.One2many('sub.contractor.daily.work','sub_contarctor_id')
	purchase_ids = fields.Many2many('purchase.order', string="Purchase")
	site_purchase_ids = fields.Many2many('site.purchase','partner_daily_statement_id',string="Material Request")
	estimate_id = fields.Many2one('project.task', string="Estimation")
	task_ids = fields.Many2many('project.task.line',string="Task")
	move_ids = fields.Many2many('stock.move',string="Material Transfer")
	picking_ids = fields.Many2many('stock.picking',string="Material Receipts")
	todays_ids = fields.One2many('todays.work.details', 'todays_id', string="Todays Work")
	view_details=fields.Boolean('View Details')

	@api.multi
	@api.depends('location_ids')
	def _get_product_ids(self):
		for record in self:
			list = []
			config = self.env['general.product.configuration'].search([], limit=1)
			for config_id in config.product_ids:
				qty = 0
				# qty = self.env['location.product.quant'].search([('location_id','=', self.location_ids.id),('product_id','=', config_id.product_id.id)], limit=1).qty

				if record.location_ids:
					product = self.env['product.product'].search([('id','=',config_id.product_id.id)])
					qty = product.with_context({'location' : record.location_ids.id}).qty_available
				list.append((0, 0, {'product_id':config_id.product_id.id,
									'quantity':qty,
									}))
			# vals.update({'product_ids': list})
			record.product_ids = list


	@api.onchange('estimate_id')
	def _onchange_estimate_id(self):
		if self.estimate_id:
			list = []
			rec = self.env['project.task.line'].search([('task_id','=',self.estimate_id.id)])
			for record in rec:
				list.append(record.id)
			return {'domain': {'task_ids': [('id', 'in', list)]}}

	@api.multi
	def set_draft(self):
		self.state = 'draft'

	@api.multi
	def cancel_entry(self):
		if self.state !='confirmed':
			records = self.env['account.move'].search([('partner_stmt_id','=',self.id)])
			if records:
				for rec in records:
					rec.button_cancel()
					rec.unlink()

		stock_move = self.env['stock.move'].search([('partner_stmt_id','=',self.id)])
		# print 'stock_move-------------------------------------', stock_move
		for move in stock_move:
			# print 'move---------------------', move
			move.state = 'draft'
			move.unlink()

		self.state = 'cancelled'


	@api.multi
	def check_entry(self):
		employee = self.env['hr.employee'].search([('id','=',1)])
		self.checked_by = self.env.user.id
		self.checked_sign = self.env.user.employee_id.sign if self.env.user.id !=1 else employee.sign
		self.state = 'checked'


	@api.multi
	@api.depends('state')
	def get_reception_trenafer(self):
		flag = 0
		if self.env.user.id == 1:
			flag = 1
		rec = self.env['cash.confirm.transfer'].search([('date','=',self.date),('state','=','pending'),('user_id','=',self.env.user.employee_id.id if flag == 0 else 1)])
		if rec:
			self.reception = True
		else:
			self.reception = False

		rec_transfer = self.env['cash.confirm.transfer'].search([('date','=',self.date),('state','=','pending'),('name','=',self.env.user.employee_id.id if flag == 0 else 1)])
		if rec_transfer:
			self.transfer = True
		else:
			self.transfer = False


	@api.multi
	def received_rs(self):
		flag = 0
		if self.env.user.id == 1:
			flag = 1
		res = {
			'name': 'Received',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'cash.confirm.transfer',
			'domain': [('user_id', '=', self.env.user.employee_id.id if flag == 0 else 1),('state','=','pending'),('date','=',self.date)],
			'target': 'new',
			'type': 'ir.actions.act_window',
			'context': {},

		}

		return res

	@api.multi
	def transferred_rs(self):
		view_ref = self.env['ir.model.data'].get_object_reference('hiworth_construction', 'tree_cash_transfer_view')
		view_id = view_ref[1] if view_ref else False
		flag = 0
		if self.env.user.id == 1:
			flag = 1
		res = {
			'name': 'Transferred',
			'view_type': 'tree',
			'view_mode': 'tree',
			'res_model': 'cash.confirm.transfer',
			'domain': [('name', '=', self.env.user.employee_id.id if flag == 0 else 1),('date','=',self.date)],
			'target': 'new',
			'view_id': view_id,
			'type': 'ir.actions.act_window',
			'context': {},

		}

		return res


	@api.multi
	def action_confirm(self):
		duplicate = self.env['partner.daily.statement'].search([('id','!=',self.id),('date','=',self.date),('employee_id','!=',self.employee_id.id),('location_ids','=',self.location_ids.id)])
		if duplicate:
			record = []
			for lines in self.line_ids:
				record.append(lines.account_id.id)
			for line in duplicate:
				for account in line.line_ids:
					if account.account_id.id in record:
						raise except_orm(_('Warning'),_('Duplicate Records In The Same Date..'))

		if self.theoretical_balance != self.balance:
			raise except_orm(_('Warning'),_('Actual Balance And Theoretical Balance Must Be Same'))

		for lines in self.received_ids:
			lines.recept_temp.unlink()
			driver_statement = lines.sudo().driver_stmt_id
			purchase = driver_statement.purchase_id
			pick_ids = []
			pick_ids += [picking.id for picking in purchase.picking_ids]

			###################################
			picking = pick_ids and pick_ids[0] or False
			# print 'test==================',picking
			picking = self.sudo().env['stock.picking'].browse(picking)
			picking.date_done = datetime.datetime.now()
			picking.sudo().approve_picking()

			values = {
				'picking_id':picking.id,
			}
			transfer = self.env['stock.transfer_details'].sudo().create(values)
			items = []
			packs = []
			if not picking.pack_operation_ids:
				picking.sudo().do_prepare_partial()
			for op in picking.sudo().pack_operation_ids:
				if op.product_id.id == lines.item_expense2.id:
					item = {
						'packop_id': op.id,
						'product_id': op.product_id.id,
						'product_uom_id': op.product_uom_id.id,
						'quantity': lines.qty,
						'price_unit': op.cost,
						'package_id': op.package_id.id,
						'lot_id': op.lot_id.id,
						'sourceloc_id': op.location_id.id,
						'destinationloc_id': op.location_dest_id.id,
						'result_package_id': op.result_package_id.id,
						'date': op.date,
						'owner_id': op.owner_id.id,
					}
					stock_move = self.env['stock.move'].sudo().search([('picking_id','=',op.picking_id.id),('product_id','=',op.product_id.id)], limit=1)
					# stock_move = self.env['stock.move'].browse(stock_move)
					item['price_unit'] = lines.rate
					item['transfer_id'] = transfer.id
					if op.product_id:
						items.append(item)
					elif op.package_id:
						packs.append(item)
			# print 'stete=================',items,picking.state
			self.env['stock.transfer_details_items'].sudo().create(items[0])
			# print 'item=================================',transfer.item_ids

			# transfer.write({'item_ids': (6, 0,  items)})
			# print 'packop wwww=================',picking.state
			transfer.sudo().do_detailed_transfer()
			# print 'packop_ids=================',packs, picking.state
			purchase.partner_ref = lines.voucher_no
			purchase.invoice_date = lines.invoice_date
			purcahse_order_line = self.sudo().env['purchase.order.line'].search([('order_id','=',purchase.id),('product_id','=',lines.item_expense2.id)])
			# print 'site_purchase_id============', purcahse_order_line.site_purchase_id
			site_purchase_id = purcahse_order_line.site_purchase_id
			site_purchase_id.invoice_date = lines.invoice_date
			site_purchase_id.invoice_no = lines.voucher_no
		# res.update(item_ids=items)
		# res.update(packop_ids=packs)
		# if purchase:
		# 	values1 = {
		# 			'source_location_id':purchase.picking_type_id.default_location_src_id.id
		# 			'date_done':datetime.datetime.now()
		# 			'date':datetime.datetime.now()
		# 			'min_date':datetime.datetime.now()
		# 			'origin':purchase.name
		# 		}
		# 	picking = self.env['stock.picking'].create(values1)
		# 	values2 = {
		# 			'product_id':driver_statement.item_expense2.id,
		# 			'product_uom_qty':driver_statement.qty
		# 			'price_unit':driver_statement.rate
		# 			'location_dest_id':purchase.location_id.id
		# 			'location_id':purchase.picking_type_id.default_location_src_id.id
		# 			'picking_id':picking.id
		# 	}
		# 	stock_move =
		# print 'gggg============================'
		self.state = 'confirmed'

		for line in self.item_usage_lines:
			if line.receipts != 0:
				location = self.env['stock.location'].search([('usage','=','supplier')], limit=1).id
				move_in = self.env['stock.move'].create({'name':line.product_id.id,
														 'product_id':line.product_id.id,
														 'product_uom_qty':line.receipts,
														 'product_uom':line.product_id.uom_id.id,
														 'location_id':location,
														 'location_dest_id':line.report_id.location_ids.id,
														 # 'picking_id': line.id
														 })
				move_in.action_done()

			if line.usage != 0:
				location = self.env['stock.location'].search([('usage','=','customer')], limit=1).id
				move_out = self.env['stock.move'].create({'name':line.product_id.id,
														  'product_id':line.product_id.id,
														  'product_uom_qty':line.usage,
														  'product_uom':line.product_id.uom_id.id,
														  'location_id':line.report_id.location_ids.id,
														  'location_dest_id':location,
														  # 'picking_id': line.id
														  })
				move_out.action_done()

		for collect_id in self.machinery_fuel_collection:
			location =  self.env['stock.location'].search([('usage','=', 'supplier')], limit=1)

			stock_move = self.env['stock.move'].create({'name':collect_id.product_id.id,
														'product_id':collect_id.product_id.id,
														'product_uom_qty':collect_id.quantity,
														'product_uom':collect_id.uom_id.id,
														'location_id':location.id,
														'location_dest_id':collect_id.site_id.id,
														'price_unit': collect_id.amount_per_unit,
														'partner_stmt_id': collect_id.collection_id.id,
														'mach_collection_id': collect_id.id
														})
			stock_move.action_done()

		for alloc_id in self.machinery_fuel_allocation:
			location =  self.env['stock.location'].search([('name','=', 'Product Consumed'),('usage','=', 'inventory')], limit=1)

			stock_move = self.env['stock.move'].create({'name':alloc_id.product_id.id,
														'product_id':alloc_id.product_id.id,
														'product_uom_qty':alloc_id.quantity,
														'product_uom':alloc_id.uom_id.id,
														'location_id':alloc_id.site_id.id,
														'location_dest_id':location.id,
														'partner_stmt_id': alloc_id.allocation_id.id,
														'mach_allocation_id': alloc_id.id
														})
			stock_move.action_done()

		for transfer_id in self.fuel_transfer_ids:

			stock_move = self.env['stock.move'].create({'name':transfer_id.product_id.id,
														'product_id':transfer_id.product_id.id,
														'product_uom_qty':transfer_id.transfer_quantity,
														'product_uom':transfer_id.uom_id.id,
														'location_id':transfer_id.site_id.id,
														'location_dest_id':transfer_id.to_location_id.id,
														'partner_stmt_id': transfer_id.transfer_id.id,
														'fuel_transfer_id': transfer_id.id
														})
			stock_move.action_done()


	@api.multi
	def cash_transfer(self):
		view_ref = self.env['ir.model.data'].get_object_reference('hiworth_construction', 'view_cash_transfer_amount')
		view_id = view_ref[1] if view_ref else False
		res = {
			'type': 'ir.actions.act_window',
			'name': _('Cash Transfer'),
			'res_model': 'cash.transfer',
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': view_id,
			'target': 'new',
			'context': {'default_name':self.employee_id.id}
		}

		return res

	@api.multi
	def view_transfer(self):
		res = {
			'name': 'Cash Transferred',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'cash.confirm.transfer',
			'domain': ['|',('name', '=', self.employee_id.id),('date','=',self.date)],
			'target': 'current',
			'type': 'ir.actions.act_window',
			'context': {},

		}

		return res

	@api.multi
	def view_receipt(self):
		res = {
			'name': 'Cash Transferred',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'cash.confirm.transfer',
			'domain': [('user_id', '=', self.employee_id.id),('date','=',self.date)],
			'target': 'current',
			'type': 'ir.actions.act_window',
			'context': {},

		}

		return res


	@api.multi
	def approve_entry(self):
		move_line = self.env['account.move.line']
		move = self.env['account.move']
		move_vals = {}
		move_line_list = []
		journal = self.env['account.journal'].sudo().search([('name','=','Miscellaneous Journal')])
		if not journal:
			raise except_orm(_('Warning'),_('Please Create Journal With name Miscellaneous Journal'))
		if len(journal) > 1:
			raise except_orm(_('Warning'),_('Multiple Journal with same name(Miscellaneous Journal)'))
		for rec in self:
			# values = {'journal_id':journal.id,'partner_daily_stmt_id':self.id,'project_id':self.project_id.id,'date':self.date, 'type':'payment'}
			move_vals = {'journal_id': journal.id,
						 'company_id': self.env.user.company_id.id,
						 'date': self.date
						 }
			move_line_list = []
			if rec.attendance_ids:
				
				account = self.env['account.account'].search([('name','=','Labour Expense')])
				for labour in rec.attendance_ids:
					labour_total = 0
					for line in labour.line_ids:
						labour_total += line.total
			
					move_line_list.append((0, 0, {'name': labour.category_id.name,
										  'account_id': account.id,
										  'debit': labour_total,
										  'credit': 0,
										  }))
			
			if rec.purchase_ids:
				purchase_total = 0
				for purchase in rec.purchase_ids:
					purchase_total = purchase.amount_total
					move_line_list.append((0, 0, {'name': purchase.name,
											  'account_id': purchase.account_id.id,
											  'debit': purchase_total,
											  'credit': 0,
											  }))
			
			if rec.expense_line_ids:
				expense_total = 0
				for expense in rec.expense_line_ids:
					expense_total += expense.total
					move_line_list.append((0, 0, {'name': expense.account_id.name,
											  'account_id': expense.account_id.id,
											  'debit': expense_total,
											  'credit': 0,
											  }))
			for rent_line in rec.rent_vehicle_stmts:
				if rent_line.advance != 0:
					if not rec.employee_id.petty_cash_account:
						raise except_orm(_('Warning'), _('You Have To Configure Supervisor Petty Account..!!'))
					if not rent_line.vehicle_no.vehicle_under.property_account_payable:
						raise except_orm(_('Warning'),
										 _('You Have To Configure Payable Account of Rent Vehicle Owner..!!'))
					move_line_list.append((0, 0, {'name': 'Advance Rent Vehicle',
												  'account_id': rent_line.vehicle_no.vehicle_under.property_account_payable.id,
												  'debit': rent_line.advance,
												  'credit': 0,
												  }))
				if rent_line.rent:
					if not rent_line.vehicle_no.vehicle_under.property_account_payable:
						raise except_orm(_('Warning'),
										 _('You Have To Configure Payable Account of Rent Vehicle Owner..!!'))
					
					move_line_list.append((0, 0, {'name': 'Rent Vehicle',
												  'account_id': rent_line.vehicle_no.vehicle_under.property_account_payable.id,
												  'debit': rent_line.rent,
												  'credit': 0,
												  }))
				
				if rent_line.diesel != 0:
					# fuel_taxes_ids = [i.id for i in rent_line.fuel_tax_ids]
					if rent_line.based_on == 'per_day':
						if not rent_line.diesel_pump.property_account_payable:
							raise except_orm(_('Warning'),
											 _('You Have To Configure Payable Account of Diesel Pump..!!'))
						
						move_line_list.append((0, 0, {'name': 'Diesel Per Day',
													  'account_id': rent_line.diesel_pump.property_account_payable.id,
													  'debit': rent_line.diesel,
													  'credit': 0,
													  }))
				if rent_line.based_on == 'per_km':
					if not rent_line.diesel_pump.property_account_payable:
						raise except_orm(_('Warning'), _('You Have To Configure Payable Account of Diesel Pump..!!'))
					if not rent_line.vehicle_no.vehicle_under.property_account_payable:
						raise except_orm(_('Warning'), _('You Have To Configure Payable Account of Vehicle Owner..!!'))
					
					move_line_list.append((0, 0, {'name': 'Diesel Per Km',
												  'account_id': rent_line.diesel_pump.property_account_payable.id,
												  'debit': rent_line.diesel,
												  'credit': 0,
												  }))
				if rent_line.full_supply == False:
					if rent_line.direct_crusher == True:
						move_line_list.append((0, 0, {'name': 'Material Cost',
													  'account_id': rent_line.crusher.property_account_payable.id,
													  'debit': rent_line.invoice_value,
													  'credit': 0,
													  }))
						
						
					if rent_line.direct_crusher == False:
						
						move_line_list.append((0, 0, {'name': 'Material Cost',
													  'account_id': rent_line.crusher.property_account_payable.id,
													  'debit': rent_line.invoice_value,
													  'credit': 0,
													  }))
					
				if rent_line.full_supply == True:
					if rent_line.direct_crusher == True:
						move_line_list.append((0, 0, {'name': 'Full Supply With Crusher Balance',
													  'account_id': rent_line.vehicle_no.vehicle_under.property_account_payable.id,
													  'debit': rent_line.invoice_value,
													  'credit': 0,
													  }))
			if rec.operator_daily_stmts:
				for operator_line in rec.operator_daily_stmts:
					
					if not operator_line.machinery_id.related_account:
						raise osv.except_osv(_('Error!'), _("Please Configure Corresponding Machinery Account."))
					
					# Expense
					
					expenses = 0
					for expense_line in operator_line.expense_line:
						expenses += expense_line.payment
					
					move_line_list.append((0, 0, {'name': 'Operator Expenses',
												  'account_id': operator_line.machinery_id.related_account.id,
												  'debit': expenses,
												  'credit': 0,
												  }))
					move_line_list.append((0, 0, {'name': 'Machinery Rent',
												  'account_id': operator_line.machinery_id.related_account.id,
												  'debit': operator_line.machinery_rent,
												  'credit': 0,
												  }))
					
					if not operator_line.employee_id.payment_account:
						raise osv.except_osv(_('Error!'), _("Please Configure Corresponding Operator Account."))
					
					move_line_list.append((0, 0, {'name': 'Operator Wage',
												  'account_id': operator_line.employee_id.payment_account.id,
												  'debit': operator_line.machinery_rent,
												  'credit': 0,
												  }))
					
					
					if operator_line.advance != 0:
						if not rec.employee_id.petty_cash_account:
							raise except_orm(_('Warning'), _('You Have To Configure Supervisor Petty Account..!!'))
						if not operator_line.employee_id.payment_account:
							raise except_orm(_('Warning'), _('You Have To Configure Operator Payable Account..!!'))
						
						move_line_list.append((0, 0, {'name': 'Operator Advance',
													  'account_id': operator_line.employee_id.payment_account.id,
													  'debit': operator_line.advance,
													  'credit': 0,
													  }))
			
			if rec.machinery_fuel_collection:
				for collect_id in rec.machinery_fuel_collection:
					move_line_list.append((0, 0, {'name': 'Fuel Purchase',
												  'account_id': collect_id.pump_id.property_account_payable.id,
												  'debit': collect_id.total_amount,
												  'credit': 0,
												  }))
		
					
					
			if rec.machinery_fuel_allocation:
				for alloc_id in rec.machinery_fuel_allocation:
					move_line_list.append((0, 0, {'name': 'Fuel Allocation',
												  'account_id': alloc_id.machinery_id.related_account.id,
												  'debit': alloc_id.total_amount,
												  'credit': 0,
												  }))
					
			
			if rec.fuel_transfer_ids:
				for transfer_id in rec.fuel_transfer_ids:
					move_line_list.append((0, 0, {'name': 'Fuel Transfer',
												  'account_id': transfer_id.to_location_id.related_account.id,
												  'debit': transfer_id.total_amount,
												  'credit': 0,
												  }))
		if self.expense != 0:
			move_line_list.append((0, 0, {'name': 'Expense',
									  'account_id': self.account_id.id,
									  'debit': 0,
									  'credit': self.expense,
									  }))
		move_vals.update({'line_id': move_line_list})
		print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr",move_vals
		move_id = move.create(move_vals)
		move_id.button_validate()
		self.state = 'approved'
		employee = self.env['hr.employee'].search([('id','=',1)])
		self.approved_by = self.env.user.id
		self.approved_sign = self.env.user.employee_id.sign if self.env.user.id != 1 else employee.sign






	@api.model
	def create(self,vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('partner.daily.statement')
		if vals.get('date'):
			if len(self.env['partner.daily.statement'].search([('employee_id','=',self.env.user.employee_id.id),('date','=',vals.get('date'))])) > 0:
				raise osv.except_osv(_('Error!'),_("Already created daily statement for today."))
		result = super(PartnerDailyStatement, self).create(vals)
		# if vals['date'] and vals['location_ids']:
		# 	if vals['state'] == 'draft':
		# 		rec = self.env['reception.temporary'].sudo().search([('date','=',vals['date']),('to_id','=',vals['location_ids'])])
		# 		if rec:
		# 			line_ids = []
		# 			for line in rec:
		# 				values = {
		# 				'from_id2':line.from_id2.id,
		# 				'item_expense2':line.item_expense2.id,
		# 				'qty':line.qty,
		# 				'rate':line.rate,
		# 				'vehicle_id':line.vehicle_id.id,
		# 				'remarks':line.remarks,
		# 				'driver_stmt_id':line.driver_stmt_id.id,
		# 				'total':line.total,
		# 				'recept_temp':line.id,
		# 				'voucher_no':line.voucher_no,
		# 				'contractor_id':line.contractor_id.id,
		# 				'rent':line.rent,
		# 				'start_km':line.start_km,
		# 				'end_km':line.end_km,
		# 				'total_km':line.total_km,
		# 				'status': 'new'
		# 				}
		# 				line_ids.append((0, False, values ))
		# 			result.received_ids = line_ids
		result.sudo().employee_id.current_location_id = self.env['partner.daily.statement'].search([('employee_id','=',result.employee_id.id)], order='date desc', limit=1).location_ids.id

		return result



	@api.multi
	def write(self, vals):
		if vals.get('location_ids'):
			latest = self.env['partner.daily.statement'].search([('employee_id','=',self.employee_id.id)], order='date desc', limit=1)
			if latest.id != self.id:
				self.sudo().employee_id.current_location_id = latest.location_ids.id
			if latest.id == self.id:
				self.sudo().employee_id.current_location_id = vals.get('location_ids')
		result = super(PartnerDailyStatement, self).write(vals)
		return result



class PayLabour(models.Model):
	_name = 'pay.labour'

	to_id = fields.Many2one('account.account')
	amount = fields.Float('Amount')
	labour_id = fields.Many2one('partner.daily.statement')


	@api.onchange('amount','to_id')
	def onchange_payment(self):
		if self.amount != False or self.amount != 0:
			if self.to_id:
				if self.to_id.balance1 < self.amount:
					self.amount = self.to_id.balance1
					return {
						'warning': {
							'title': 'Warning',
							'message': "You cannot give amount greater than due."
						}
					}



class ApproverLine(models.TransientModel):
	_name = 'approver.lines'

	name = fields.Many2one('partner.daily.statement')
	approver = fields.Many2one('res.users',string='Approvers')
	tick = fields.Boolean('Tick If No Other Approvers')

	@api.multi
	def next_approvers(self):
		if self.tick and self.approver:
			raise osv.except_osv(_('Error!'), _('Error: Either Tick Or Enter Next approver'))

		if self.name.next_approver.id == self.env.user.id:
			self.env['supervisor.statement.approvers'].create({'approver':self.name.next_approver.id,'status':'approved','approver_id':self.name.id,'date':fields.Datetime.now()})
		else:
			raise osv.except_osv(_('Error!'), _('Error: You Are Not The Next Approver'))
		if self.tick == True:
			self.name.state = 'approved'
		else:
			if self.approver:
				self.name.next_approver = self.approver.id
			else:
				raise osv.except_osv(_('Error!'), _('Error: Either Tick Or Enter Next approver'))
		return True


	@api.multi
	def confirm_approvers(self):
		self.name.next_approver = self.approver.id
		self.name.state = 'approve_in_progress'
		return True



class PartnerDailyStatementLine(models.Model):
	_name = 'partner.daily.statement.line'


	@api.onchange('quantity')
	def onchange_quantity(self):
		if self.quantity == 0:
			self.total = 0
		else:
			if self.total != 0 and self.rate != 0 and self.quantity != round((self.total / self.rate),2):
				self.quantity = 0.0
				return {
					'warning': {
						'title': 'Warning',
						'message': "For Entering value to Quantity field, Rate or Total should be Zero"
					}
				}
			if self.quantity != 0 and self.rate != 0:
				if self.rate*self.quantity != self.total:
					pass
				if self.total == 0.0:
					self.total = round((self.quantity * self.rate),2)
			if self.total != 0 and self.quantity != 0:
				if self.rate == 0.0:
					self.rate = round((self.total / self.quantity),2)


	@api.onchange('rate')
	def onchange_rate(self):
		if self.rate == 0:
			self.total = 0
		else:
			if self.total != 0 and self.quantity != 0 and self.rate != round((self.total / self.quantity),2):
				self.rate = 0.0
				return {
					'warning': {
						'title': 'Warning',
						'message': "For Entering value to Rate field, Quantity or Total should be Zero."
					}
				}
			if self.quantity != 0 and self.rate != 0:
				if self.rate*self.quantity != self.total:
					pass
				if self.total == 0.0:
					self.total = round((self.quantity * self.rate),2)
			if self.total != 0 and self.rate != 0:
				if self.quantity == 0.0:
					self.quantity = round((self.total / self.rate),2)



	@api.onchange('total')
	def onchange_total(self):
		if self.total != 0:
			if self.rate*self.quantity != self.total:
				if self.rate != 0 and self.quantity != 0:
					self.total = 0.0
					return {
						'warning': {
							'title': 'Warning',
							'message': "For Entering value to Total field, Quantity or Rate should be Zero."
						}
					}
				elif self.rate == 0 and self.quantity != 0:
					self.rate = round((self.total / self.quantity),2)
				elif self.quantity == 0 and self.rate != 0:
					self.quantity = round((self.total / self.rate),2)
				else:
					pass

	# @api.onchange('quantity','rate')
	# def onchange_qty_rate(self):
	# 	if self.quantity and self.rate:
	# 		self.total = self.quantity * self.rate
	# 	if self.quantity == 0 or self.rate == 0:
	# 		self.total = 0


	# @api.onchange('total','quantity')
	# def onchange_qty_total(self):
	# 	if self.total and self.quantity:
	# 		self.rate = self.total / self.quantity

	# @api.onchange('rate','total')
	# def onchange_rate_total(self):
	# 	if self.rate and self.total:
	# 		self.quantity = self.total / self.rate


	@api.onchange('payment')
	def onchange_payment(self):
		if self.payment != 0 and self.account_id.user_type.report_type in ['asset','liability']:
			if self.mason_bool == True:
				total = 0
				for lines in self.mason_lines:
					total += lines.total
				if self.account_id.balance1+total < self.payment:
					self.payment = self.account_id.balance1+total
					return {
						'warning': {
							'title': 'Warning',
							'message': "You cannot give amount greater than due."
						}
					}

			else:
				if self.line_bool == True:
					if self.account_id.balance1+self.total < self.payment:
						self.payment = self.account_id.balance1+self.rate
						return {
							'warning': {
								'title': 'Warning',
								'message': "You cannot give amount greater than due."
							}
						}






	@api.multi
	@api.depends('qty_entered','particular_ids')
	def compute_qty(self):
		for rec in self:
			if rec.particular_ids:
				rec.qty += len(rec.particular_ids)
			if rec.qty_entered:
				rec.qty = rec.qty_entered

	@api.multi
	@api.depends('particular_ids','rate')
	def compute_rate_char(self):
		for rec in self:
			if rec.mason_bool == True:
				rate = ''
				for lines in rec.mason_lines:
					qyt_rount=int(lines.qty)
					rate = rate + ("+" if rate !='' else '')+str(qyt_rount)+"*"+ str(lines.rate)
				rec.rate_char = rate
			else:
				if rec.line_bool == True:
					rec.rate_char = str(rec.account_id.rate)
				else:
					rate1 = ''
					for lines in rec.particular_ids:
						if lines.account_id.category_id.name == 'Labour':
							qyt_rount=int(lines.qty)
							# rec.rep +=qyt_rount
							# rate1 = str(rec.rep)+"*"+ str(lines.rate)
							rate1 = rate1 + ("+" if rate1 !='' else '')+str(qyt_rount)+"*"+ str(lines.rate)
					rec.rate_char = rate1


		# if rec.particular_ids:
		# 	list = []
		# 	rate_char = ''
		# 	for line in rec.particular_ids:
		# 		if line.category_id.id not in list:
		# 			list.append(line.category_id.id)
		# 	temp = False
		# 	for category in list:
		# 		stmt_part = self.env['statement.particular'].search([('line_id','=',rec.id),('category_id','=',category)])
		# 		if stmt_part:
		# 			if temp == True:
		# 				rate_char += '+'+str(len(stmt_part))+"*"+str(stmt_part[0].rate)
		# 			if temp == False:
		# 				rate_char += str(len(stmt_part))+"*"+str(stmt_part[0].rate)
		# 				temp = True
		# 	rec.rate_char = rate_char



	@api.multi
	@api.depends('qty_entered','particular_ids','rate','qty_no')
	def compute_qty_char(self):
		for rec in self:
			if rec.mason_bool == True:
				code = ''
				for lines in rec.mason_lines:
					qyt_rount=int(lines.qty)
					# print '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@2================',qyt_rount
					code = code +("+" if code != '' else '' )+str(qyt_rount)+ "*"+str(lines.name.code)
					rec.qty_no+=qyt_rount
				# print '================================',rec.qty_no
				rec.qty_char = code
			else:
				if rec.line_bool == True:
					rec.qty_char = str(rec.quantity)
				else:
					code1 = ''
					for lines in rec.particular_ids:
						# print '=========================',lines.account_id.category_id.name
						if lines.account_id.category_id.name == 'Labour':
							qyt_rount=int(lines.qty)
							rec.qty_no+=qyt_rount
							code1 = str(rec.qty_no)
							# code1 = code1 +("+" if code1 != '' else '' )+str(qyt_rount)+ "*"+str(lines.account_id.category_id.code) 
							# print '================================',rec.qty_no

							rec.qty_char = code1


		# if rec.particular_ids:
		# 	print "ggggggggggggggggggggggggggggggggggggggggggggggggg"
		# 	list = []
		# 	for line in rec.particular_ids:
		# 		final_list = filter(lambda x: x['code'] == line.category_id.code, list)
		# 		if len(final_list) == 0:
		# 			list.append({'code':line.category_id.code, 'qty':1})
		# 		if len(final_list) != 0:
		# 			a = list.index(final_list[0])
		# 			list[a]['qty'] += 1
		# 		# list.append(final_list)
		# 	temp = False
		# 	for lines in list:
		# 		if temp == True:
		# 			rec.qty_char = rec.qty_char+'+'+str(lines['qty'])+lines['code']
		# 		if temp == False:
		# 			rec.qty_char = str(lines['qty'])+lines['code']
		# 			temp = True
		# 	if rec.qty_entered:
		# 		rec.qty_char = str(rec.qty_entered)+rec.category_id.code



	@api.depends('payment','particular_ids',)
	def get_total_payment(self):
		for rec in self:
			if rec.particular_ids:
				for lines in rec.particular_ids:
					rec.payment_total += lines.payment
			else:
				rec.payment_total = rec.payment

	@api.multi
	@api.depends('account_id')
	def compute_category(self):
		for rec in self:
			if rec.account_id:
				rec.category_id = rec.account_id.category_id.id



	@api.onchange('account_id')
	def account_onchange(self):
		if self.account_id.is_mason == True:
			self.mason_bool = True
			record = []
			for lines in self.account_id.mason_line:
				record.append({'name':lines.name.id,'rate':lines.rate})
			self.mason_lines = record
		else:
			self.mason_bool = False

	qty_no=fields.Integer('Total Qty',compute='compute_qty_char')
	rep = fields.Integer('Rep')
	account_id = fields.Many2one('account.account', 'Account')
	quantity = fields.Float('Quantity')
	total = fields.Float('Total')
	# category_id = fields.Many2one('labour.category', 'Category')
	category_id = fields.Many2one('labour.category', compute='compute_category', store=True, string='Category')
	line_bool = fields.Boolean(default=True)
	is_labour = fields.Boolean(default=False)
	item_id = fields.Many2one('daily.statement.item', 'Item')
	qty_entered = fields.Float('Qty')
	qty = fields.Float(compute='compute_qty', store=True, string='Qty')
	qty_char = fields.Char(compute='compute_qty_char', store=True, string="Qty")
	# rate_char = fields.Char(compute='compute_amount_char', store=True, string="Rate")
	rate = fields.Float('Rate')
	rate_char = fields.Char('Rate',compute="compute_rate_char")
	payment = fields.Float('Payment')
	payment_total = fields.Float('Payment',compute="get_total_payment")
	vr_no = fields.Char('VR No.')
	remarks = fields.Text('Remarks')
	report_id = fields.Many2one('partner.daily.statement', 'Report')
	particular_ids = fields.One2many('statement.particular', 'line_id', 'Particulars')
	account_type = fields.Selection([
		('ie','Income/Expense'),
		('al','Asset/Liability')], 'Account Type')
	mason_bool = fields.Boolean(default=False)
	mason_lines = fields.One2many('mason.line','line_ids')
	expense = fields.Boolean(default=False)

	@api.onchange('account_id','category_id')
	def onchange_account_id(self):
		if self.account_id:
			rec = self.env['account.account'].search([('parent_id','=',self.account_id.id)])
			if rec:
				self.line_bool = False
				# self.qty_entered = 0
				self.rate = 0
				self.category_id = False
			else:
				self.line_bool = True
			if self.account_id:
				self.rate = self.account_id.rate
			if self.account_id.is_labour == True:
				self.is_labour = True
			else:
				self.is_labour = False
			if self.account_id.user_type.report_type in ['income','expense']:
				self.account_type = 'ie'
			if self.account_id.user_type.report_type in ['asset','liability']:
				self.account_type = 'al'

# @api.multi
# def action_validate(self):
# 	for rec in self:
# 		print 'aaaaaaaaaaaaaaaaa'



class SupervisorStatementApprovers(models.Model):
	_name = 'supervisor.statement.approvers'

	approver_id = fields.Many2one('partner.daily.statement')
	approver = fields.Many2one('res.users','Approver')
	status = fields.Selection([('not_approved','Not Approved'),('approved','Approved')],default='not_approved',string="Approver")
	date = fields.Datetime('Date')


class OperatorDailyStatement(models.Model):
	_name = 'operator.daily.statement'

	operator_id = fields.Many2one('partner.daily.statement')
	date = fields.Date('Date')
	employee_id = fields.Many2one('hr.employee', string="Operator", domain=[('user_category','=','operators')])
	machinery_id = fields.Many2one('fleet.vehicle', string="Machinery", domain=[('machinery','=',True)])
	start_reading = fields.Float('Start Reading')
	end_reading = fields.Float('End Reading')
	working_hours = fields.Float('Working Hours', compute="compute_operator_details")
	quantity = fields.Float('Quantity',default="1")
	machinery_rent = fields.Float('Machinery Rent', compute="compute_operator_details")
	operator_amt = fields.Float('Operator Amount', compute="compute_operator_details")
	expense = fields.Float('Machinery Expense', compute="compute_total_expense")
	expense_line = fields.One2many('driver.daily.expense','expense_id')
	advance = fields.Float('Advance')
	running_km = fields.Float('Running Km')

	_defaults = {
		'date': date.today()
	}


	@api.onchange('running_km','start_reading','end_reading','machinery_id')
	def onchange_readings(self):
		record = self.env['operator.daily.statement'].search([('machinery_id','=', self.machinery_id.id)], order="date desc",limit=1)
		print 'record-------------------------', record.date,record.start_reading,record.end_reading
		if record:
			if self.running_km:
				self.start_reading = record.end_reading + self.running_km
			else:
				self.start_reading = record.end_reading



	@api.onchange('quantity')
	def onchange_quantity(self):
		if self.quantity not in [0,1,1.5,2]:
			raise osv.except_osv(_('Error!'),_("The quantity given is not allowed."))

	@api.multi
	@api.depends('start_reading','end_reading','machinery_id','employee_id','quantity')
	def compute_operator_details(self):
		for record in self:
			record.working_hours = round((record.end_reading - record.start_reading),2)
			record.operator_amt = round((record.employee_id.per_day_eicher_rate * record.quantity),2)
			if record.machinery_id.mach_rent_type == 'hours':
				record.machinery_rent = round((record.machinery_id.per_day_rent * record.working_hours),2)
			else:
				record.machinery_rent = round((record.machinery_id.per_day_rent),2)


	@api.multi
	@api.depends('expense_line')
	def compute_total_expense(self):
		for record in self:
			for expense in record.expense_line:
				record.expense += expense.total

class StatementParticular(models.Model):
	_name = 'statement.particular'

	@api.one
	def onchange_payment(self):
		if self.qty and self.rate:
			self.payment = self.qty * self.rate

	@api.multi
	@api.depends('qty','rate')
	def compute_total(self):
		for rec in self:
			if rec.qty and rec.rate:
				rec.total = rec.qty * rec.rate


	@api.onchange('payment')
	def onchange_payment(self):
		if self.payment != 0 and self.account_id.user_type.report_type in ['asset','liability']:
			if self.account_id.balance1+self.total < self.payment:
				self.payment = self.account_id.balance1+self.rate
				return {
					'warning': {
						'title': 'Warning',
						'message': "You cannot give amount greater than due."
					}
				}

	@api.multi
	@api.depends('account_id')
	def compute_rate(self):
		for rec in self:
			if rec.account_id:
				rec.rate = rec.account_id.rate

	@api.multi
	@api.depends('account_id')
	def compute_category(self):
		for rec in self:
			if rec.account_id:
				rec.category_id = rec.account_id.category_id.id


	account_id = fields.Many2one('account.account', 'Account')
	qty = fields.Float('Qty')
	payment = fields.Float('Payment')
	total = fields.Float(compute='compute_total', string="Total")
	category_id = fields.Many2one('labour.category', compute='compute_category', store=True, string='Category')
	rate = fields.Float(compute='compute_rate', store=True, string='Rate')
	line_id = fields.Many2one('partner.daily.statement.line', 'Line')


	@api.onchange("account_id")
	def onchange_accounts_id_line(self):
		# res = {}
		record = self.env['account.account'].search([('parent_id','=',self.line_id.account_id.id)])
		ids = []
		for item in record:
			ids.append(item.id)
		return {'domain': {'account_id': [('id', 'in', ids)]}}

class ItemUsage(models.Model):
	_name = 'item.usage'

	@api.multi
	@api.depends('pre_qty','receipts')
	def compute_total(self):
		for rec in self:
			rec.total = rec.pre_qty + rec.receipts

	@api.multi
	@api.depends('total','usage')
	def compute_balance(self):
		for rec in self:
			rec.balance = round((rec.total - rec.usage),2)


	product_categ = fields.Many2one('pricelist.master', string="Product Category")
	product_id = fields.Many2one('product.product', 'Item')
	item_of_work = fields.Many2one('item.of.work', string="Item of Work")
	uom_id = fields.Many2one('product.uom', string="Unit")
	pre_qty = fields.Float('Pre. Balance',readonly=True)
	req_qty = fields.Float(string="Theoritical Quantity")
	receipts = fields.Float('Receipts')
	total = fields.Float(compute='compute_total', store=True, string='Total')
	usage = fields.Float('Usage')
	balance = fields.Float(compute='compute_balance', store=True, string='Balance')
	report_id = fields.Many2one('partner.daily.statement', 'Report')
	rqrd_id = fields.Many2one('partner.daily.statement', 'Required')
	rqrd_qty = fields.Float('Required Qty')
	name = fields.Char('Description')
	date = fields.Date('Date',default=fields.Date.today())

	@api.onchange("item_of_work")
	def onchange_item_of_work(self):
		if self.report_id.task_ids:
			ids = []
			for val in self.report_id.task_ids:
				ids.append(val.name.id)
			return {'domain': {'item_of_work': [('id','in', ids)]}}


	@api.model
	def create(self, vals):
		result = super(ItemUsage, self).create(vals)
		if result.pre_qty == 0:
			qty = 0
			if result.report_id.location_ids:
				product = self.env['product.product'].search([('id','=',result.product_id.id)])
				qty = product.with_context({'location' : result.report_id.location_ids.id}).qty_available

			# if result.product_id:
			# 	rec = self.env['stock.history'].search([('product_id','=',result.product_id.id),('location_id','=',result.report_id.location_ids.id)])
			# 	for vals in rec:
			# 		qty += vals.quantity
			# 	result.pre_qty = qty
			result.pre_qty = qty
		return result


	@api.onchange("usage")
	def onchange_usage(self):
		if self.usage:
			if self.usage > self.total:
				self.usage = self.total
				return {
					'warning': {
						'title': 'Warning',
						'message': "You cannot give usage greater than total quantity."
					}
				}

	@api.onchange("product_id")
	def onchange_pre_qty(self):
		qty = 0
		record = self.env['stock.history'].search([('location_id','=',self.report_id.location_ids.id)])
		if self.product_id:
			rec = self.env['stock.history'].search([('product_id','=',self.product_id.id),('location_id','=',self.report_id.location_ids.id)])
			# if self.item_of_work:
			# 	theoritical = self.env['material.estimation'].search([('item_id','=',self.product_id.id),('material_id.name','=',self.item_of_work.id),('material_id.task_id','=',self.report_id.estimate_id.id)])
			# 	self.req_qty = theoritical.qty 
			for vals in rec:
				qty += vals.quantity
		self.pre_qty = qty
		list = []
		for item in record:
			list.append(item.product_id.id)
		return {'domain': {'product_id': [('id', 'in', list)]}}


class NextDayWork(models.Model):
	_name = 'next.day.work'


	name = fields.Char('Name')

class NextDayWorkItems(models.Model):
	_name = 'next.day.work.items'


	product_id = fields.Many2one('product.product')
	uom_id = fields.Many2one('product.uom', 'Item')
	qty = fields.Float('Qty')

class DailyStatementItem(models.Model):
	_name = 'daily.statement.item'

	@api.constrains('name')
	def _check_duplicate_name(self):
		names = self.search([])
		for c in names:
			if self.id != c.id:
				if self.name.lower() == c.name.lower() or self.name.lower().replace(" ", "") == c.name.lower().replace(" ", ""):
					raise osv.except_osv(_('Error!'), _('Error: name must be unique'))
			else:
				pass


	name = fields.Char('Name')
# rate = fields.Float('Rate')



class LabourCategory(models.Model):
	_name = 'labour.category'

	name = fields.Char(string='Name')
	code = fields.Char(string='Code', size=3)
	wage = fields.Float(string='Wage')
	pricelist_id = fields.Many2one('pricelist.master', string="Product Category")

class AccountAccount(models.Model):
	_inherit = 'account.account'

	is_labour = fields.Boolean('Is Labour')
	category_id = fields.Many2one('labour.category', 'Category')


class DailyStatementItemReceived(models.Model):
	_name = 'daily.statement.item.received'

	@api.multi
	def approve_line(self):
		self.status = 'accepted'
		self.sudo().driver_stmt_id.status = 'accepted'
		self.sudo().driver_stmt_id.line_id._get_driver_status1()

	@api.multi
	def reject_line(self):
		self.status = 'rejected'
		# self.sudo().driver_stmt_id.line_id.driver_status1 = 'reject'
		self.sudo().driver_stmt_id.status = 'rejected'
		if not self.rejection_remarks:
			raise osv.except_osv(_('Error!'), _('Please enter the reason for rejection'))

		self.sudo().driver_stmt_id.rejection_remarks = self.rejection_remarks
		self.sudo().driver_stmt_id.line_id._get_driver_status1()
	# self.driver_stmt_id.line_id.cancel_entry()
	# self.driver_stmt_id.line_id.set_draft()


	name = fields.Char('Name')
	particulars = fields.Char('Particulars')
	from_id2 = fields.Many2one('res.partner','From')
	item_expense2 = fields.Many2one('product.product','Item')
	qty = fields.Float('Qty',default=1)
	rate = fields.Float('Rate')
	total = fields.Float('Total')
	vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')
	start_km = fields.Float('Start KM')
	end_km = fields.Float('End KM')

	total_km = fields.Float('Total KM')
	# payment = fields.Float('Payment')
	voucher_no = fields.Char('Voucher No')
	contractor_id = fields.Many2one('res.company.new', 'Contractor')
	rent = fields.Float('Rent')
	remarks  = fields.Char('Remarks')
	received_id = fields.Many2one('partner.daily.statement', 'Required')
	driver_stmt_id = fields.Many2one('driver.daily.statement.line')
	status = fields.Selection([('new','New'),('accepted','Accepted'),('rejected','Rejected')],readonly=True)
	recept_temp = fields.Many2one('reception.temporary')
	rejection_remarks  = fields.Text('Reason for Rejection')
	purchase_id = fields.Many2one('purchase.order', 'Purchase')
	invoice_date  = fields.Date('Invoice Date')

class GeneralFuelConfigurationWizard(models.TransientModel):

	_name = 'general.fuel.configuration.wizard'

	product_id = fields.Many2one('product.product', 'Fuel', domain=[('fuel_ok','=','True')])

	@api.model
	def default_get(self, vals):
		res = super(GeneralFuelConfigurationWizard, self).default_get(vals)
		config = self.env['general.fuel.configuration'].search([], limit=1)

		res.update({
			'product_id': config.product_id.id,
		})
		return res

	@api.multi
	def excecute(self):
		# print 'test=========================', asd
		config = self.env['general.fuel.configuration'].search([])
		for line in config:
			line.unlink()
		self.env['general.fuel.configuration'].create({'product_id': self.product_id.id,})
		return {
			'type': 'ir.actions.client',
			'tag': 'reload',
		}


	@api.multi
	def cancel(self):
		return {
			'type': 'ir.actions.client',
			'tag': 'reload',
		}



class GeneralFuelConfiguration(models.Model):
	_name = 'general.fuel.configuration'


	product_id = fields.Many2one('product.product', 'Fuel', domain=[('fuel_ok','=','True')])


class GeneralProductConfiguration(models.Model):
	_name = 'general.product.configuration'


	product_ids = fields.One2many('general.product.configuration.line','line_id')

class GeneralProductConfigurationLine(models.Model):
	_name = 'general.product.configuration.line'


	line_id = fields.Many2one('general.product.configuration')
	product_id = fields.Many2one('product.product', 'Product')



class PartnerStmtProducts(models.Model):
	_name = 'partner.statement.products'


	line_id = fields.Many2one('partner.daily.statement')
	product_id = fields.Many2one('product.product', 'Product')
	quantity = fields.Float('Quantity')

class FuelTransfer1(models.Model):
	_name = 'partner.fuel.transfer'


	transfer_id = fields.Many2one('partner.daily.statement')
	product_id = fields.Many2one('product.product', 'Fuel', domain=[('fuel_ok','=',True)])
	uom_id = fields.Many2one('product.uom','Unit', related="product_id.uom_id")
	available_quantity = fields.Float('Available Quantity', compute="_get_available_qty", store=True)
	current_quantity = fields.Float('Current Quantity', compute="_get_current_qty", store=True)
	transfer_quantity = fields.Float('Transfer Quantity')
	site_id = fields.Many2one('stock.location', string="From Location", domain=[('usage','=','internal')])
	supervisor_id = fields.Many2one('hr.employee')
	to_location_id = fields.Many2one('stock.location', string="To Location", domain=[('usage','=','internal')])
	amount_per_unit = fields.Float('Amount Per Unit', compute="get_amount", store=True)
	total_amount = fields.Float('Total Amount', compute="get_amount", store=True)
	stock_move_id = fields.Many2one('stock.move')
	account_move_id = fields.Many2one('account.move')

	@api.multi
	@api.depends('product_id','transfer_quantity')
	def _get_current_qty(self):
		for record in self:
			record.current_quantity = record.available_quantity - record.transfer_quantity

	@api.multi
	@api.depends('product_id','site_id')
	def _get_available_qty(self):
		for record in self:
			if record.site_id:
				product = self.env['product.product'].search([('id','=',record.product_id.id)])
				record.available_quantity = product.with_context({'location' : record.site_id.id}).qty_available
			# print 'qty----------------------------------------------------', product.with_context({'location' : record.site_id.id}).qty_available

	@api.multi
	@api.depends('transfer_quantity')
	def get_amount(self):
		for record in self:
			amt = 0
			transfer_quantity = record.transfer_quantity
			quants = self.env['stock.quant'].search([('product_id','=', record.product_id.id),('location_id','=', record.site_id.id)], order="in_date asc")
			for quant_id in quants:
				# print 'quant_id----------------------------------', quant_id.qty, transfer_quantity
				if transfer_quantity > 0:
					if quant_id.qty >= transfer_quantity:
						if quant_id.qty != 0:
							amt += (quant_id.inventory_value/quant_id.qty) * transfer_quantity
							transfer_quantity = transfer_quantity - quant_id.qty
						# print 'amt11-----------------------------------', amt
					else:
						amt += quant_id.inventory_value
						transfer_quantity = transfer_quantity - quant_id.qty
					# print 'amt22-----------------------------------', amt

			record.total_amount = amt
			if record.transfer_quantity != 0:
				record.amount_per_unit = amt/record.transfer_quantity



	@api.model
	def default_get(self, default_fields):
		vals = super(FuelTransfer1, self).default_get(default_fields)
		user = self.env['res.users'].search([('id','=',self.env.user.id)])
		if user:
			if user.employee_id:
				vals.update({'supervisor_id' : user.employee_id.id,
							 })
			if not user.employee_id and user.id != 1:
				raise osv.except_osv(_('Error!'),_("User and Employee is not linked."))

		return vals

	@api.onchange('transfer_quantity')
	def onchange_qty(self):
		if not self.transfer_quantity <= self.available_quantity:
			raise osv.except_osv(_('Error!'),_("You cannot transfer fuel more than available quantity."))


class TodayWork(models.Model):
	_name = 'today.work'

	today_work_id = fields.Many2one('partner.daily.statement')
	tomrw_work_id = fields.Many2one('partner.daily.statement')

	item_of_work = fields.Many2one('item.of.work', string="Item of Work")
	contractor_id = fields.Char(string="Name of Contractor")
	qty = fields.Float(string="Quantity")
	unit = fields.Many2one('product.uom',string="Units")
	note = fields.Text(string="Description")

	@api.onchange("item_of_work")
	def onchange_item_of_work(self):
		if self.tomrw_work_id.task_ids:
			ids = []
			for val in self.tomrw_work_id.task_ids:
				ids.append(val.name.id)
			return {'domain': {'item_of_work': [('id','in', ids)]}}

class MaterialConsumption(models.Model):
	_name = 'material.consumption'


	material_id = fields.Many2one('partner.daily.statement')

	item_id = fields.Many2one('pricelist.master', string="Material Consumption")
	item_of_work = fields.Many2one('item.of.work', string="Item of Work")
	theoritical_qty = fields.Float(string="Theoritical Quantity")
	actual_qty = fields.Float(string="Actual Quantity")
	unit = fields.Many2one('product.uom',string="Unit")



class ManpowerConsumption(models.Model):
	_name = 'manpower.consumption'

	# @api.one
	# @api.depends('category_id','item_of_work','manpower_id')
	# def _get_actual_qty(self):
	# 	if self.manpower_id:
	# 		if self.category_id and self.item_of_work:
	# 			cnt = 0
	# 			other_qty = 0

	# 			# manpower = self.env['manpower.estimation'].search([('estimate_id','=',self.manpower_id.estimate_id.id),('work_id','=',self.item_of_work.id),('category_id','=',self.category_id.id)])
	# 			master = self.env['labour.attendance'].search([('attendance_id','=',self.manpower_id.id),('category_id','=',self.category_id.id)])
	# 			labours = self.env['labour.attendance.line'].search([('line_id','=',master.id),('item_of_work','=',self.item_of_work.id),('attendance','=',True)])
	# 			others = self.env['group.attendance'].search([('group_id','=',self.manpower_id.id),('category_id','=',self.category_id.id),('item_of_work','=',self.item_of_work.id)])
	# 			for y in labours:
	# 				cnt += 1
	# 			for x in others:
	# 				other_qty += x.count

	# 			self.actual_qty = cnt + other_qty

	@api.multi
	@api.depends('pricelist_id','item_of_work')
	def _get_theoritical_qty(self):
		for val in self:
			if val.pricelist_id and val.item_of_work:
				master = self.env['todays.work.details'].search([('todays_id','=',val.manpower_id.id),('name','=',val.item_of_work.id)])
				for m in master:
					resource = self.env['todays.work.resources'].search([('resource_id','=',val.pricelist_id.id),('resource_line_id','=',m.id)])
					if resource:
						val.theoritical_qty = resource.tot_qty



	manpower_id = fields.Many2one('partner.daily.statement')

	# item_id = fields.Many2one('hr.employee', string="Manpower Consumption")
	item_of_work = fields.Many2one('item.of.work', string="Item of Work")
	category_id = fields.Many2one('labour.category', string="Category")
	pricelist_id = fields.Many2one('pricelist.master', string="Product Category")
	theoritical_qty = fields.Float(string="Theoritical Quantity", compute='_get_theoritical_qty')
	actual_qty = fields.Float(string="Actual Quantity")
	unit = fields.Many2one('product.uom',string="Unit")



# @api.one
# def unlink(self):
# 	return super(ManpowerConsumption, self).unlink()

# @api.onchange('item_of_work','category_id','manpower_id')
# def _onchange_category_id(self):

# 	if self.category_id and self.item_of_work:
# 		total_qty = 0
# 		manpower = self.env['manpower.estimation'].search([('estimate_id','=',self.manpower_id.estimate_id.id),('work_id','=',self.item_of_work.id),('category_id','=',self.category_id.id)])

# 		for val in manpower:
# 			total_qty += val.qty

# 		self.theoritical_qty = total_qty


class LabourMaster(models.Model):
	_name = 'labour.master'

	number = fields.Char(string="Number")
	name = fields.Char(string="Name")
	category_id = fields.Many2one('labour.category', string="Category")
	wage = fields.Float(string="Wage")
	grade = fields.Char(string="Grade")

	@api.onchange('category_id')
	def _onchange_category_id(self):
		if self.category_id:
			self.wage = self.category_id.wage


class LabourAttendance(models.Model):
	_name = 'labour.attendance'
	_rec_name = 'category_id'

	date = fields.Date(string="Date")
	category_id = fields.Many2one('labour.category', string="Category")

	@api.depends('wage', 'allowance','no_labours')
	def _compute_total(self):
		for rec in self:
			rec.total = (rec.wage + rec.allowance) * rec.no_labours

	name_of_worker = fields.Many2one('labour.master', string="Name of Worker")
	grade = fields.Char(string="Grade")
	item_of_work = fields.Many2one('item.of.work', string="Item of Work Engaged")
	detail_of_work = fields.Char(string="Detail of Work")
	attendance = fields.Boolean(string="Attendance")
	wage = fields.Float(string="Wage")
	allowance = fields.Float(string="Allowance")
	total = fields.Float(string="Total", compute='_compute_total')
	no_labours = fields.Float('No of Labours')
	line_ids = fields.One2many('labour.attendance.line', 'line_id')
	attendance_id = fields.Many2one('partner.daily.statement')


	@api.onchange('category_id')
	def _onchange_category_id(self):
		labour_list = []
		res = {}
		if self.category_id:
			labours = self.env['labour.master'].search([('category_id','=',self.category_id.id)])
			for val in labours:
				res = {
					'name_of_worker':val.id,
					'grade':val.grade,
					'attendance':True,
					'wage':val.wage
				}
				labour_list.append(res)
			self.line_ids = labour_list


	@api.model
	def create(self, vals):
		result = super(LabourAttendance, self).create(vals)
		values = self.line_ids.search([('line_id','=',result.id),('attendance','=',False)])
		for val in values:
			val.unlink()
		return result



class LabourAttendanceLine(models.Model):
	_name = 'labour.attendance.line'
	_rec_name = 'name_of_worker'

	line_id = fields.Many2one('labour.attendance')
	name_of_worker = fields.Many2one('labour.master', string="Name of Worker")
	grade = fields.Char(string="Grade")
	item_of_work = fields.Many2one('item.of.work', string="Item of Work Engaged")
	detail_of_work = fields.Char(string="Detail of Work")
	attendance = fields.Boolean(string="Attendance")
	wage = fields.Float(string="Wage")
	allowance = fields.Float(string="Allowance")
	total = fields.Float(string="Total",compute='_compute_total')

	# report_id = fields.Many2one(related="line_id.attendance_id")



	@api.depends('wage','allowance')
	def _compute_total(self):
		for rec in self:
			rec.total = rec.wage + rec.allowance






	# @api.multi
	# @api.onchange("item_of_work")
	# def onchange_item_of_work(self):
	# 	for val in self:	
	# 		# print '---------------------------------val--------------------------------',val.id	
	# 		# print '---------------------------------type(val.id)--------------------------------',type(val) 	
	# 		if val.line_id.attendance_id.task_ids:			
	# 			ids = []
	# 			for v in val.line_id.attendance_id.task_ids:
	# 				ids.append(v.name.id)
	# 				# print '======================================ids============================>',ids
	# 				# print '======================================type(ids)============================>',type(ids)
	# 			# print '******************ids***************************', ids
	# 			# print '******************type(ids)***************************',type(ids)
	# 			return {'domain': {'item_of_work': [('id','in', ids)]}}


	@api.multi
	def unlink(self):
		return super(LabourAttendanceLine, self).unlink()

class GroupAttendance(models.Model):
	_name = 'group.attendance'
	_rec_name = 'category_id'

	group_id = fields.Many2one('partner.daily.statement')

	category_id = fields.Many2one('labour.category', string="Category")
	contractor_id = fields.Many2one('res.partner', 'Name of Contractor', domain = [('contractor','=',True)])
	item_of_work = fields.Many2one('item.of.work', string="Item of Work Engaged")
	count = fields.Integer(string="Number of Labours")

	@api.onchange("item_of_work")
	def onchange_item_of_work(self):
		if self.group_id.task_ids:
			ids = []
			for val in self.group_id.task_ids:
				ids.append(val.name.id)
			return {'domain': {'item_of_work': [('id','in', ids)]}}


class OtherAttendance(models.Model):
	_name = 'other.attendance'
	_rec_name = 'category_id'

	other_id = fields.Many2one('partner.daily.statement')

	category_id = fields.Many2one('labour.category', string="Category")
	contractor_id = fields.Many2one('res.partner', 'Name of Contractor', domain = [('contractor','=',True)])
	item_of_work = fields.Many2one('item.of.work', string="Item of Work Engaged")
	count = fields.Integer(string="Number of Labours")

class TodaysWorkDetails(models.Model):
	_name = "todays.work.details"


	@api.multi
	@api.depends('detailed_ids')
	def _get_total_qty(self):
		for value in self:
			qty = 0.0
			for val in value.detailed_ids:
				qty += val.qty

			value.qty = qty

	@api.onchange("name")
	def onchange_name(self):
		if self.name and self.todays_id.project_id:
			self.resource_ids.unlink()
			items = self.env['main.data'].search([('project_id','=',self.todays_id.project_id.id),('name','=',self.name.id)])
			vals = []
			for item in items:
				for data in item.data_ids:
					vals.append((0, 0,{
						'resource_line_id':self.id,
						'resource_id':data.item_id.id,
						'qty':data.qty,
						'categ_id':data.item_id.categ_id.id,
						'uom_id':data.item_id.unit.id,
					}))

				ids = []
				for val in vals:
					ids.append(val[2]['resource_id'])

				for subdata in item.sub_ids:
					for sub in subdata.subdata_ids:
						if sub.item_id.id not in ids:
							vals.append((0, 0,{
								'resource_line_id':self.id,
								'resource_id':sub.item_id.id,
								'qty':sub.qty,
								'categ_id':sub.item_id.categ_id.id,
								'uom_id':sub.item_id.unit.id,
							}))


			self.resource_ids = vals

	todays_id = fields.Many2one('partner.daily.statement')

	name = fields.Many2one('item.of.work', string="Item of Work")
	category = fields.Many2one('task.category', string="Category")
	qty = fields.Float(string="Quantity", compute='_get_total_qty')
	unit = fields.Many2one('product.uom', string="Unit")
	note = fields.Text(string="Description")

	detailed_ids = fields.One2many("todays.work.line", 'line_id')
	resource_ids = fields.One2many('todays.work.resources','resource_line_id')

class TodaysWorkLine(models.Model):
	_name = "todays.work.line"

	@api.one
	@api.depends('nos_x','nos_y','length','breadth','depth')
	def _get_qty(self):

		self.qty = self.nos_x * self.nos_y * self.length * self.breadth * self.depth


	line_id = fields.Many2one('todays.work.details')

	name = fields.Char(string="Description")
	nos_x = fields.Integer(string="Nos", default=1)
	nos_y = fields.Integer(string="Nos", default=1)
	length = fields.Float(string="L", default=1)
	breadth = fields.Float(string="B", default=1)
	depth = fields.Float(string="D", default=1)
	qty = fields.Float(string="Quantity", compute='_get_qty')


class TodaysWorkLineResources(models.Model):
	_name = "todays.work.resources"

	@api.one
	@api.depends('resource_line_id.qty','qty')
	def _compute_qty(self):
		if self.qty and self.resource_line_id.qty:
			self.tot_qty = self.qty * self.resource_line_id.qty

	resource_line_id = fields.Many2one('todays.work.details')

	resource_id = fields.Many2one('pricelist.master', string="Resource")
	qty = fields.Float(string="Quantity")
	categ_id = fields.Many2one('task.category', string='Category')
	uom_id = fields.Many2one('product.uom', string='Unit')
	tot_qty = fields.Float(string="Total Quantity", compute='_compute_qty')

	@api.one
	def unlink(self):
		return super(TodaysWorkLineResources, self).unlink()

class SubcontractorDailyWork(models.Model):
	_name = 'sub.contractor.daily.work'
	_rec_name = 'contractor'

	sub_contarctor_id = fields.Many2one('partner.daily.statement')
	date=fields.Date('Date')
	project_id = fields.Many2one('project.project', 'Project')
	detail_of_work = fields.Char(string="Detail of Work")
	no_labour = fields.Float('No of Labours')
	wage = fields.Float('Daily Wage')
	attendance = fields.Boolean(string="Attendance")
	item_of_work = fields.Many2one('item.of.work', string="Item of Work Engaged")
	contractor = fields.Many2one('res.company.new', 'Contractor')
	total = fields.Float(string="Total", compute='_compute_total')


	@api.depends('wage','no_labour')
	def _compute_total(self):
		for rec in self:
			rec.total = rec.wage * rec.no_labour