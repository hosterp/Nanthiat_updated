from openerp import models, fields, api, _
from openerp.exceptions import except_orm, ValidationError
import datetime
from datetime import date
from datetime import time
class InventoryDepartment(models.Model):
	_name = 'inventory.department'

	name = fields.Many2one('product.product','Product')
	date = fields.Date('Date')
	location_id = fields.Many2one('stock.location','Location')
	qty = fields.Float('Quantity')
	rate = fields.Float('Rate')
	inventory_value = fields.Float('Inventory Value')
	department = fields.Selection([('general','General'),
								   ('vehicle','Vehicle'),
								   ('telecom','Telecom'),
								   ('interlocks','Interlocks'),
								   ('workshop','Workshop')],string="Department")
	site_purchase_id = fields.Many2one('site.purchase')



class SitePurchasegroup(models.Model):
	_name = 'site.purchase.group'

	@api.multi
	def merge_orders(self):
		site_requests = self.env.context.get('active_ids')
		record = []
		supplier = False
		for request in site_requests:
			site_record = self.env['site.purchase'].search([('id','=',request)])
			if site_record:
				if site_record.state != 'approved2':
					raise except_orm(_('Warning'),_('Site Requests Must Be In Draft State.Please Check..!!'))           
				if not site_record.expected_supplier:
					raise except_orm(_('Warning'),_('One of the site requests not have supplier.Please configure..!!'))         
				if supplier == False:
					supplier = site_record.expected_supplier.id
				elif supplier != site_record.expected_supplier.id:
					raise except_orm(_('Warning'),_('Supplers are different..!!'))          
				
				line_record = {
					'product_id':site_record.item_id.id,
					'product_qty':site_record.quantity,
					'name':site_record.item_id.name,
					'site_purchase_id':site_record.id,
					'product_uom':site_record.unit.id,
					'pro_old_price':site_record.item_id.standard_price,
					'unit_price':site_record.item_id.standard_price,
					'price_unit':site_record.item_id.standard_price,
					'location_id':False,
					'account_id':site_record.item_id.categ_id.stock_account_id.id,
					'state':'draft'
					}
				record.append((0, False, line_record ))


		view_ref = self.env['ir.model.data'].get_object_reference('purchase', 'purchase_order_form')
		view_id = view_ref[1] if view_ref else False
		res = {
		   'type': 'ir.actions.act_window',
		   'name': _('Purchase Order'),
		   'res_model': 'purchase.order',
		   'view_type': 'form',
		   'view_mode': 'form',
		   'view_id': view_id,
		   'target': 'current',
		   'context': {'default_partner_id':supplier,'default_order_line':record,'default_date_order':fields.Date.today(),'default_state':'draft'}
	   }

		return res


class SitePurchase(models.Model):
	_name = 'site.purchase'
	_order = 'id desc'


	@api.onchange('quantity')
	def onchange_quantity_rate(self):
		if self.quantity == 0:
			self.estimated_amt = 0
		else:
			if self.estimated_amt != 0 and self.rate != 0 and self.quantity != round((self.estimated_amt / self.rate),2):
				self.quantity = 0.0
				return {
					'warning': {
						'title': 'Warning',
						'message': "For Entering value to quantity field, Rate or estimated_amt should be Zero"
					}
				}
			if self.quantity != 0 and self.rate != 0:
				if self.rate*self.quantity != self.estimated_amt:
					pass
				if self.estimated_amt == 0.0:
					self.estimated_amt = round((self.quantity * self.rate),2)
			if self.estimated_amt != 0 and self.quantity != 0:
				if self.rate == 0.0:
					self.rate = round((self.estimated_amt / self.quantity),2)

	@api.onchange('rate')
	def onchange_rate_estimated_amt(self):
		if self.rate == 0:
			self.estimated_amt = 0
		else:
			if self.estimated_amt != 0 and self.quantity != 0 and self.rate != round((self.estimated_amt / self.quantity),2):
				self.rate = 0.0
				return {
					'warning': {
						'title': 'Warning',
						'message': "For Entering value to Rate field, quantity or estimated_amt should be Zero."
					}
				}
			if self.quantity != 0 and self.rate != 0:
				if self.rate*self.quantity != self.estimated_amt:
					pass
				if self.estimated_amt == 0.0:
					self.estimated_amt = round((self.quantity * self.rate),2)
			if self.estimated_amt != 0 and self.rate != 0:
				if self.quantity == 0.0:
					self.quantity = round((self.estimated_amt / self.rate),2)


	@api.onchange('estimated_amt')
	def onchange_qty_estimated_amt(self):
		if self.estimated_amt != 0:
			if self.rate*self.quantity != self.estimated_amt:
				if self.rate != 0 and self.quantity != 0:
					self.estimated_amt = 0.0
					return {
						'warning': {
							'title': 'Warning',
							'message': "For Entering value to estimated_amt field, quantity or Rate should be Zero."
						}
					}
				elif self.rate == 0 and self.quantity != 0:
					self.rate = round((self.estimated_amt / self.quantity),2)
				elif self.quantity == 0 and self.rate != 0:
					self.quantity = round((self.estimated_amt / self.rate),2)
				else:
					pass


	@api.onchange('item_id')
	def onchange_product_id(self):

		if self.item_id:
			self.unit = self.item_id.uom_id.id
			self.desc = self.item_id.name


	# @api.onchange('min_expected_date','max_expected_date')
	# def onchange_min_expected_date1(self):
	# 	current_date = datetime.now().date()
	# 	if self.min_expected_date and (self.min_expected_date < str(current_date)):
	# 		self.min_expected_date = False

	# 	if self.max_expected_date and (self.max_expected_date < str(current_date)):
	# 		self.max_expected_date = False





	@api.model
	def default_get(self, default_fields):
		vals = super(SitePurchase, self).default_get(default_fields)
		user = self.env['res.users'].search([('id','=',self.env.user.id)])
		if user:
			vals.update({'responsible' : user.id})
			if user.employee_id or user.id == 1:
				vals.update({'supervisor_id' : user.employee_id.id if user.id != 1 else self.env['hr.employee'].search([('id','=',1)]).id })

		return vals


	@api.multi
	@api.depends('tax_ids','received_total')
	def get_tax_amount(self):
		for lines in self:
			taxi = 0
			taxe = 0
			for tax in lines.tax_ids:
				if tax.price_include == True:
					taxi = tax.amount
				if tax.price_include == False:
					taxe += tax.amount
			lines.tax_amount = (lines.received_total)/(1+taxi)*(taxi+taxe)
			lines.sub_total = (lines.received_total)/(1+taxi)
			lines.total_amount = lines.tax_amount + lines.sub_total

	@api.multi
	@api.depends('received_qty','received_rate')
	def get_received_total(self):
		for rec in self:
			rec.received_total = rec.received_qty*rec.received_rate


	name = fields.Char('Name',readonly=True)
	supervisor_id = fields.Many2one('hr.employee','User')
	responsible = fields.Many2one('res.users','Responsible',readonly=True)
	order_date = fields.Datetime('Order Date',readonly=False)#default=datetime.now().date()
	min_expected_date = fields.Date('Minimum Expected Date',required=True)
	max_expected_date = fields.Date('Maximum Expected Date')
	received_date = fields.Date('Received Date')
	item_id = fields.Many2one('product.product','Item')
	quantity = fields.Float('Quantity')
	unit = fields.Many2one('product.uom','Unit')
	req_list = fields.One2many('request.item.list', 'req_list_line', 'Req List')
	request_not_in_draft = fields.Boolean('flag')
	storekeeper_purchase = fields.Boolean('Store Keeper Purchase')
	state = fields.Selection([('draft','Draft'),
							  ('confirm','Requested'),
							  ('approved1','Approved By PM'),
							  ('approved2','Approved By DGM'),
							  ('approved3','Approved By Admin'),
							  ('processing','Processing'),
							  ('received','Received'),
							  ('cancel','Cancelled')],default="draft",string="Status")
	site_id = fields.Many2one('partner.daily.statement')
	desc = fields.Char('Description')
	site = fields.Many2one('stock.location','Location')
	received_qty = fields.Float('Received Qty')
	received_rate = fields.Float('Received Rate')
	received_total = fields.Float(compute='get_received_total', string='Amount')
	general_purchase = fields.Boolean(default=False)
	vehicle_purchase = fields.Boolean(default=False)
	telecom_purchase = fields.Boolean(default=False)
	interlocks_purchase = fields.Boolean(default=False)
	workshop_purchase = fields.Boolean(default=False)
	bitumen_purchase = fields.Boolean(default=False)
	# expected_supplier = fields.Many2one('res.partner','Supplier')
	rate = fields.Float('Rate')
	partner_daily_statement_id = fields.Many2one('partner.daily.statement',string="Daily Statement")
	estimated_amt = fields.Float('Estimated Amount')
	purchase_manager = fields.Many2one('res.users','Purchase Manager')
	sign_general_manager = fields.Binary('Sign')
	project_manager = fields.Many2one('res.users','Project Manager')
	sign_purchase_manager = fields.Binary('Sign')
	invoice_no = fields.Char('Invoice No.')
	invoice_date = fields.Date('Invoice Date')
	stock_move_id = fields.Many2one('stock.move', 'Stock Move')
	account_move_id = fields.Many2one('account.move', 'Journal Entry')
	tax_ids = fields.Many2many('account.tax',string="Tax")
	tax_amount = fields.Float('Tax Amount',compute="get_tax_amount")
	sub_total = fields.Float('Sub Total',compute="get_tax_amount")
	total_amount = fields.Float('Total',compute="get_tax_amount")
	bitumen_agent = fields.Many2one('res.partner', 'Agent')
	vehicle_agent = fields.Many2one('res.partner', 'Vehicle Agent')
	bank_id = fields.Many2one('res.partner.bank', 'Bank')
	doc_no = fields.Char('Doc No.')
	project_id = fields.Many2one('project.project', 'Project')
	req_no = fields.Char('Req No')
	remarks = fields.Text(string="Remarks")
	user_category = fields.Selection([('admin', 'Super User'),
									  ('project_manager', 'Project Manager'),
									  ('supervisor', 'Supervisor(Civil)'),
									  ('DGM', 'DGM'),
									  ], string='User Category', required=True, default='supervisor')

	@api.onchange('project_id')
	def onchange_project_id(self):
		if self.project_id:
			self.site=self.project_id.location_id.id

	@api.multi
	def cancel_process(self):
		if self.state != 'received':
			self.state = 'cancel'
		else:
			inv_record = self.env['inventory.department'].search([('site_purchase_id','=',self.id)])
			if inv_record:
				inv_record.unlink()

		move = self.stock_move_id
		if move:
			quants = self.env['stock.quant'].search([('reservation_id','=', move.id)])
			for quant in move.quant_ids:
				quant.sudo().qty = 0.0
			move.sudo().state = 'draft'
			# move.product_id.product_tmpl_id.sudo().qty_available = move.product_id.product_tmpl_id.qty_available - move.product_uom_qty
			move.sudo().unlink()

		account_move = self.account_move_id
		if account_move:
			account_move.button_cancel()
			account_move.unlink()

		self.state = 'cancel'

	@api.multi
	def set_draft(self):
		self.state = 'draft'
		self.request_not_in_draft = False


	@api.multi
	def confirm_purchase(self):
		if len(self.req_list):
			for r in self.req_list:
				if r.requested_quantity < 1:
					raise except_orm(_('Warning'), ('Request qty is zero for the product '+str(r.item_id.name)))
			self.state = 'confirm'
			# self.user_category = 'project_manager'
			self.request_not_in_draft = True
			self.env['popup.notifications'].sudo().create({
				'name':self.project_id.user_id.id,
				'status':'draft',
				'message':"You have a material request to approve from"+' '+ self.supervisor_id.name})
		else:
			raise except_orm(_('Warning'), ('The Request items must be filled..'))

	@api.multi
	def generate_po_stock(self):
		purchase_supplier = []
		stock_supplier = []
		comapany_location = self.env['stock.location'].search([('name', '=', 'Stock')])

		for line in self.req_list:
			if not line.expected_supplier:
				raise except_orm(_('Operation not allowed!'),
								 _("No supplier Selected for product "+ str(line.item_id.name)))
			if not line.stock_type:
				raise except_orm(_('Operation not allowed!'), _("You should consider giving a stock type for product "+ str(line.item_id.name)))
			if line.stock_type == 'supplier_stock' and line.expected_supplier not in purchase_supplier:
				purchase_supplier.append(line.expected_supplier)
			else:
				if line.expected_supplier not in stock_supplier:
					stock_supplier.append(line.expected_supplier)
		for s in purchase_supplier:
			purchase_lines = []
			for req in self.req_list:
				if req.expected_supplier.id == s.id and req.stock_type == 'supplier_stock':
					purchase_lines.append((0, 0, {
						'product_id': req.item_id.id,
						'name': req.desc,
						'required_qty': req.quantity,
						'product_uom': req.unit.id,
						'expected_rate': req.rate,
						'price_unit': 0.0,
						'account_id': self.env['account.account'].search([('name', '=', 'Purchase')]).id,
						'date_planned': self.min_expected_date,
						'site_purchase_id': self.id,
					}))
			order = self.env['purchase.order'].create({
				'partner_id': s.id,
				'request_id': self.id,
				'supervisor_id': self.supervisor_id.id,
				'location_id': self.site.id,
				'account_id': s.property_account_payable.id,
				'minimum_planned_date': self.min_expected_date,
				'maximum_planned_date': self.max_expected_date,
				'request_date': self.order_date,
				'order_date': '',
				'pricelist_id': s.property_product_pricelist_purchase.id,
				'order_line': purchase_lines,
			})
		for s in stock_supplier:
			stock_lines = []
			for req in self.req_list:
				if req.expected_supplier.id == s.id and req.stock_type == 'company_stock':
					stock_lines.append((0, 0, {
						'location_id': comapany_location.id,
						'project_id': self.project_id.id,
						'product_id': req.item_id.id,
						'available_qty': req.item_id.with_context({'location' : comapany_location.id}).qty_available,
						'name': req.desc,
						'product_uom_qty': req.quantity,
						'product_uom': req.unit.id,
						'account_id': self.site.related_account.id,
						'location_dest_id': self.site.id,
					}))
			# print "stock lines=======================",stock_lines
			if stock_lines:
				stock = self.env['stock.picking'].create({
						'request_id': self.id,
						'partner_id': s.id,
						'site': self.site.id,
						'order_date': self.order_date,
						'account_id': s.property_account_payable.id,
						'supervisor_id': self.supervisor_id.id,
						'move_lines': stock_lines
					})
				# print "stock==================",stock
		self.state = 'processing'
		# self.user_category = False


	@api.multi
	def approve_purchase1(self):
		self.project_manager = self.env.user.id
		self.state = 'approved1'
		# self.user_category = 'DGM'
		self.env['popup.notifications'].sudo().create({
			'name':self.project_id.user_id.id,
			'status':'draft',
			'message':"You have a material request to approve from"+' '+ self.supervisor_id.name
		})

	@api.multi
	def approve_purchase2(self):
		self.state = 'approved2'
		# self.user_category = 'admin'
		self.env['popup.notifications'].sudo().create({
			'name':self.project_id.user_id.id,
			'status':'draft',
			'message':"You have a material request to approve from"+' '+ self.supervisor_id.name
		})

	@api.multi
	def approve_purchase3(self):
		self.state = 'approved3'
		# self.user_category = False
		self.env['popup.notifications'].sudo().create({
			'name':self.project_id.user_id.id,
			'status':'draft',
			'message':"You have a material request from"+' '+ self.supervisor_id.name
		})

	@api.multi
	def view_invoices(self):
		record =  self.env['hiworth.invoice'].search([('site_purchase_id','=',self.id)])

		if record:
			res_id = record[0].id
		else:
			res_id = False
		res = {
			'name': 'Supplier Invoices',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'hiworth.invoice',
			'domain': [('line_id', '=', self.id)],
			'res_id': res_id,
			'target': 'current',
			'type': 'ir.actions.act_window',
			'view_id': self.env.ref('hiworth_construction.hiworth_invoice_form').id,
			'context': {'default_inv_type': 'out', 'type2': 'out'},

		}

		return res

	@api.model
	def create(self, vals):
		
		if vals.get('supervisor_id') == False:
			user = self.env['res.users'].sudo().search([('id','=',self.env.user.id)])
			if user:
				if user.employee_id or user.id == 1:
					vals['supervisor_id'] = user.employee_id.id if user.id !=1 else self.env['hr.employee'].search([('id','=',1)]).id
				else:
					raise except_orm(_('Warning'),_('User have To Be Linked With Employee.'))

		if vals.get('site') == False:
			if vals.get('site_id'):
				vals['site'] = self.env['partner.daily.statement'].search([('id','=',vals['site_id'])]).location_ids.id

		result = super(SitePurchase, self).create(vals)
		if result.name == False:
			if result.general_purchase == True:
				result.name = str('GPR-')+self.env['ir.sequence'].next_by_code('site.purchase') or '/'
			if result.vehicle_purchase == True:
				result.name = str('VPR-')+self.env['ir.sequence'].next_by_code('site.purchase') or '/'
			if result.telecom_purchase == True:
				result.name = str('TPR-')+self.env['ir.sequence'].next_by_code('site.purchase') or '/'
			if result.interlocks_purchase == True:
				result.name = str('IPR-')+self.env['ir.sequence'].next_by_code('site.purchase') or '/'
			if result.workshop_purchase == True:
				result.name = str('QPR-')+self.env['ir.sequence'].next_by_code('site.purchase') or '/'
			result.order_date = fields.Datetime.now()
			for rec in result.req_list:
				if rec.requested_quantity == 0:
					raise except_orm(_('Warning'),_('Requested quantity must be greater than zero'))
		return result



class Request_Item_list(models.Model):
	_name = 'request.item.list'

	@api.onchange('requested_quantity')
	def onchange_requested_quantity(self):		
		if self.requested_quantity:
			self.quantity = self.requested_quantity


	req_list_line = fields.Many2one('site.purchase')
	item_id = fields.Many2one('product.product','Item')
	requested_quantity = fields.Float('Required Quantity')
	quantity = fields.Float('Approved Quantity')
	remarks = fields.Text('Remarks')
	unit = fields.Many2one('product.uom','Unit')
	rate = fields.Float('Rate')
	expected_supplier = fields.Many2one('res.partner', 'Supplier',domain=[('supplier','=',True)])
	stock_type = fields.Selection([('company_stock', 'Company Stock'), ('supplier_stock', 'Supplier Stock')])
	estimated_amt = fields.Float('Estimated Amount')
	desc = fields.Char('Description')
	request_not_in_draft = fields.Boolean('flag', related="req_list_line.request_not_in_draft")
	


	@api.onchange('stock_type')
	def onchange_stock_type(self):
		if self.stock_type == 'company_stock':
			self.expected_supplier = 82

	@api.onchange('item_id')
	def onchange_product_id(self):

		if self.item_id:
			self.unit = self.item_id.uom_id.id
			self.desc = self.item_id.name


class BcplAccountDetails(models.Model):
	_name = 'bcpl.account.details'


	item = fields.Char('Item')
	invoice_no=fields.Integer('Invoice No')
	doc = fields.Integer('Doc')
	order_date= fields.Date('Order Date')
	supplier = fields.Many2one('res.partner','Supplier')
	site_name = fields.Char('Site Name')
	qty = fields.Integer('Qty')
	rate = fields.Float('Rate')
	amount = fields.Float('Amount',compute= 'onchange_amount')
	agent = fields.Char('Agent')
	vehicle_no = fields.Char('Vehicle No')
	date = fields.Date('Date')
	bank = fields.Char('Bank')
	total_amount = fields.Float('Toatal Amount')


	@api.onchange('qty','rate')
	def onchange_amount(self):
		self.amount= self.qty*self.rate



