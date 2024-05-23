from openerp.exceptions import except_orm, ValidationError
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import Warning as UserError
from openerp import models, fields, api, _
from openerp import workflow
import time
import datetime
from datetime import date
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import timedelta
from pychart.arrow import default
from openerp.osv import osv, expression

class AccountMoveNewApi(models.Model):

	_inherit = 'account.move'

	@api.one
	def delete_all_related_cash_ban_expense_entry(self):

		if self.id:
			bank_books = self.env['bank.book.line'].search([('move_id', '=', self.id)])
			cash_books = self.env['cash.book.line'].search([('move_id', '=', self.id)])
			expense_books = self.env['expense.book.line'].search([('move_id', '=', self.id)])
			if bank_books:
				for b in bank_books:
					b.unlink()
			if cash_books:
				for c in cash_books:
					c.unlink()
			if expense_books:
				for e in expense_books:
					e.unlink()

class CashBook(models.Model):
	_name = 'cash.book'
	_rec_name = 'date'

	READONLY_STATES = {
		'close': [('readonly', True)],
	}

	@api.onchange('account_id')
	def onchange_account(self):
		if self.account_id:
			self.opening = self.account_id.balance


	@api.model
	def default_get(self, fields):
		res = super(CashBook, self).default_get(fields)
		line_id = self.env['cash.book.configuration.line'].search([('cashbook_config_id','=',self.env.user.company_id.id)], limit=1, order='id asc')
		if line_id:
			# return line_id.account_id.id
			res.update({'account_id': line_id.account_id.id})
		return res

	@api.multi
	@api.depends('move_lines')
	def compute_current_balance(self):
		for rec in self:
			debit = 0
			credit = 0
			for lines in rec.move_lines:
				debit += lines.debit
				credit += lines.credit
			rec.current_balance = rec.opening + (debit - credit)

	@api.multi
	@api.depends('actual_balance')
	def compute_difference(self):
		if self.actual_balance:
			if self.actual_balance == self.current_balance:
				self.is_difference = False
			else:
				self.is_difference = True
				cash_book_config = self.env['res.company'].search([], limit=1)
				if cash_book_config:
					self.write_off_account = cash_book_config.write_off_account.id
		else:
			self.is_difference = False


	date = fields.Date('Date', states=READONLY_STATES)
	user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user, states=READONLY_STATES)
	account_id = fields.Many2one('account.account', 'Account', states=READONLY_STATES)
	opening = fields.Float('Opening Balance')
	move_lines = fields.One2many('cash.book.line', 'cash_book_id', 'Transactions', states=READONLY_STATES)
	state = fields.Selection([('draft', 'Draft'),('open', 'Open'),('close', 'Closed')], 'State', default='draft')
	balance = fields.Float('Balance', states=READONLY_STATES)
	remarks = fields.Text('Remarks', states=READONLY_STATES)
	current_balance = fields.Float(compute='compute_current_balance', string="Balance")
	actual_balance = fields.Float('Actual Balance', states=READONLY_STATES)
	write_off_account =  fields.Many2one('account.account', 'Write Off Account', states=READONLY_STATES)
	is_difference = fields.Boolean(compute='compute_difference', string="Difference")
	company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

	@api.multi
	def action_open(self):
		for rec in self:
			rec.state = 'open'


	@api.multi
	def action_close(self):
		for rec in self:
			if rec.actual_balance != rec.current_balance:
				journal =  self.env['account.journal'].search([('type','=','general'),('company_id','=',rec.company_id.id)], limit=1)
				if not journal:
					raise UserError("Please create a journal with type 'General'.")
				move = self.env['account.move'].create({'journal_id':journal.id,'date':rec.date})

				move_line = self.env['account.move.line']
				amount = 0
				debit_account = False
				credit_account = False
				if rec.actual_balance < rec.current_balance:
					amount = rec.current_balance - rec.actual_balance
					debit_account = rec.write_off_account.id
					credit_account = rec.account_id.id
				else:
					amount = rec.actual_balance - rec.current_balance
					debit_account = rec.account_id.id
					credit_account = rec.write_off_account.id
				move_line.create({'move_id':move.id,
								  'state': 'valid',
								  'name': 'Write Off amount from '+' '+rec.user_id.name+' on'+ str(rec.date),
								  'account_id':credit_account,
								  'debit':0,
								  'credit':amount,
								  'closed':True
								})
				move_line.create({'move_id':move.id,
								  'state': 'valid',
								  'name': 'Write Off amount from '+' '+rec.user_id.name+' on'+ str(rec.date),
								  'account_id':debit_account,
								  'debit':amount,
								  'credit':0,
								  'closed':True
								})
				for lines in rec.move_lines:
					if lines.closed == True:
						lines.cash_book_id = False
				move.button_validate()
				rec.state = 'close'
			else:
				rec.state = 'close'

	@api.model
	def create(self,vals):
		result = super(CashBook, self).create(vals)
		result.opening = result.account_id.balance
		return result

class CashBookLines(models.Model):

	_name = "cash.book.line"

	cash_book_id = fields.Many2one('cash.book', 'CashBook')
	narration = fields.Char('Description')
	account_id = fields.Many2one('account.account', 'Account')
	debit = fields.Float('Debit')
	credit = fields.Float('Credit')
	closed = fields.Boolean('Closed', default=False)
	move_id = fields.Many2one('account.move', 'Journal Entry')

	def open_line_transactions(self, cr,uid,ids,args=None):
		obj = ''
		for s in self.browse(cr,uid,ids):
			obj = s
		return {
			'name': _('Transaction History'),
			'view_type': 'tree',
			'view_mode': 'tree',
			'res_model': 'account.move.line',
			'type': 'ir.actions.act_window',
			'target': 'current',
			'domain': [('account_id', '=', obj.account_id.id)],
		}

class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	def open_line_transactions(self, cr,uid,ids,args=None):
		obj = ''
		for s in self.browse(cr,uid,ids):
			obj = s
		return {
			'name': _('Transaction History'),
			'view_type': 'tree',
			'view_mode': 'tree',
			'res_model': 'account.move.line',
			'type': 'ir.actions.act_window',
			'target': 'current',
			'domain': [('account_id', '=', obj.account_id.id)],
		}

	@api.constrains('account_id')
	def _check_duplicate_account_id(self):
		if self.move_id.date:
			account_ids =  [line.account_id.id for line in self.company_id.account_ids]
			if self.account_id.id in account_ids:
				cash_book = self.env['cash.book'].search([('date','=',self.move_id.date),('account_id','=',self.account_id.id),('state','=','open')])
				if not cash_book:
					raise UserError("Please open today's cash book...........!")

	@api.model
	def create(self,vals):
		result = super(AccountMoveLine, self).create(vals)
		if result.move_id.date:
			account_ids = [line.account_id.id for line in result.company_id.account_ids]
			accounts_ids = [line.account_id.id for line in result.company_id.accounts_ids]
			# if result.account_id.id in account_ids and result.account_id.parent_id.id not in accounts_ids or result.account_id.parent_id.parent_id.id not in accounts_ids:
			cash_book = self.env['cash.book'].search(
				[('date', '=', result.move_id.date), ('account_id', '=', account_ids[0]),
				 ('state', '=', 'open')])
			if result.move_id.journal_id.default_credit_account_id.id in account_ids and not result.move_id.copy_to_expense:
				if result.account_id.id not in account_ids:
					if cash_book:
						if result.debit > 0.0:
							self.env['cash.book.line'].create({
								'cash_book_id': cash_book.id,
								'narration': result.name,
								'account_id': result.account_id.id,
								'move_id': result.move_id.id,
								'debit': 0.0,
								'credit': result.debit,
							})
						if result.credit > 0.0:
							self.env['cash.book.line'].create({
								'cash_book_id': cash_book.id,
								'narration': result.name,
								'account_id': result.account_id.id,
								'move_id': result.move_id.id,
								'debit': result.credit,
								'credit': 0.0,
							})
					else:
						raise UserError("Please open today's Cash Book...........!")
		return result


class CashBookConfigurationLine(models.Model):
	_name = 'cash.book.configuration.line'

	cashbook_config_id = fields.Many2one('res.company', 'Cashbook Configuration')
	account_id = fields.Many2one('account.account', "Account")



class ResCompany(models.Model):
	_inherit = 'res.company'

	account_ids = fields.One2many('cash.book.configuration.line', 'cashbook_config_id','Acconts fo Cash Register')
	write_off_account = fields.Many2one('account.account', 'Account for Write Off', domain=[('type','=','other')])

from openerp.osv import osv

class AccountMove(osv.osv):

	_inherit = 'account.move'

	def button_cancel(self, cr, uid, ids, context=None):
		for line in self.browse(cr, uid, ids, context=context):
			for ex in self.pool.get('cash.book.line').search(cr, uid, [('move_id', '=', line.id)]):
				if ex:
					self.pool.get('cash.book.line').browse(cr, uid, ex).unlink()
			cr.execute('UPDATE account_move_line ' \
					   'SET is_posted=False ' \
					   'WHERE move_id = %s',
					   (line.id,))
			if not line.journal_id.update_posted:
				raise osv.except_osv(_('Error!'), _(
					'You cannot modify a posted entry of this journal.\nFirst you should set the journal to allow cancelling entries.'))
		if ids:
			cr.execute('UPDATE account_move ' \
					   'SET state=%s ' \
					   'WHERE id IN %s', ('draft', tuple(ids),))

			self.invalidate_cache(cr, uid, context=context)
		return True







