from openerp import models, fields, api, _
from openerp.exceptions import except_orm, ValidationError
from openerp.osv import osv
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

class PaymentApprovals(models.Model):
	_name = 'payment.approvals'
	_rec_name = 'date'

	@api.one
	def approve(self):
		for i in self.payment_approval_line:
			if i.amount_approved == 0.0:
				i.unlink()
		self.state = 'approved'

	@api.onchange('type')
	def onchange_type(self):
		if self.type == 'supp':
			purchases = []
			for s in self.env['res.partner'].search([]):
				total = 0.0
				for p in self.env['purchase.order'].search([('partner_id', '=', s.id), ('state', '=', 'done')]):
					total += p.amount_total
				if total > 0.0:
					purchases.append((0, 0, {'supplier_id': s.id, 'amount': total}))
			self.payment_approval_line = purchases
		elif self.type == 'lab':
			labour_charge = []
			for project in self.env['project.project'].search([]):
				total = 0.0
				for sds in self.env['partner.daily.statement'].search([('project_id', '=', project.id)]):
					for a in sds.attendance_ids:
						for ll in a.line_ids:
							total += ll.wage
				if total > 0.0:
					labour_charge.append((0, 0, {'project_id': project.id, 'amount': total}))
			self.payment_approval_line = labour_charge
		elif self.type == 'ot':
			expenses = []
			for project in self.env['project.project'].search([]):
				total_exp = 0.0
				for sds in self.env['partner.daily.statement'].search([('project_id', '=', project.id)]):
					total_exp += sds.expense
				if total_exp > 0.0:
					expenses.append((0, 0, {'project_id': project.id, 'amount': total_exp}))
			self.payment_approval_line = expenses

	@api.one
	def get_total_requested_approved(self):
		total_requested = 0.0
		total_approved = 0.0
		for l in self.payment_approval_line:
			total_requested += l.amount
			total_approved += l.amount_approved
		self.total_requested = total_requested
		self.total_approved = total_approved

	date = fields.Date('Date')
	show_approvals = fields.Boolean('Show Approvals')
	type = fields.Selection([('supp', 'Supplier'), ('lab', 'Labour'), ('ot', 'Expenses')])
	payment_approval_line = fields.One2many('payment.approvals.line', 'approval_id')
	total_requested = fields.Float('Total Requested', compute="get_total_requested_approved")
	total_approved = fields.Float('Total Approved', compute="get_total_requested_approved")
	state = fields.Selection([('draft', 'Draft'), ('approved', 'Approved')], default="draft")

class PaymentApprovalsLine(models.Model):

	_name = 'payment.approvals.line'

	@api.onchange('amount_approved')
	def amount_approved_onchange(self):
		self.get_updated_balance()

	@api.multi
	def get_data(self):
		if self.approval_id.type == 'supp':
			return {
				'name': _('Approved'),
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'purchase.order',
				'type': 'ir.actions.act_window',
				'target': 'current',
				'domain': [('partner_id', '=', self.supplier_id.id), ('state', '=', 'done')],
			}

		if self.approval_id.type in ('lab', 'lot'):
			return {
				'name': _('Approved'),
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'partner.daily.statement',
				'type': 'ir.actions.act_window',
				'target': 'current',
				'domain': [('project_id', '=', self.project_id.id)],
			}

	def get_updated_balance(self):
		for s in self:
			if s.current_balance or s.amount_approved:
				s.updated_balance = s.current_balance + s.amount_approved

	approval_id = fields.Many2one('payment.approvals')
	supplier_id = fields.Many2one('res.partner', 'Supplier')
	account_id = fields.Many2one('account.account', 'Account', related="supplier_id.property_account_payable")
	project_id = fields.Many2one('project.project', 'Related Project')
	amount = fields.Float('Amount')
	current_balance = fields.Float('Previous Balance', related="supplier_id.property_account_payable.balance")
	updated_balance = fields.Float('Current Balance', compute="get_updated_balance")
	amount_approved = fields.Float('Approved Amount')
	narration = fields.Char('Narration')
