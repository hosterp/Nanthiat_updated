from openerp import models, fields, api, _

class TransferDocument(models.Model):
	_name = 'transfer.document'

	rec = fields.Many2one('customer.file.details')
	partner_id = fields.Many2one('res.partner','Transfer To')
	user_id = fields.Many2one('res.users','Send To')
	recs = fields.Many2one('my.work.report')

	@api.multi
	def send_doc(self):
		if self.user_id:
			self.recs.sent_report = self.user_id.id
			self.recs.project.work_report_man = self.user_id.id
			self.recs.state = 'send'

	@api.multi
	def transfer_doc(self):
		if self.partner_id:
			if self.partner_id.customer == True:
				self.rec.write({'state': 'pend_cust'})
			else:

				self.env['customer.file.details'].sudo().create({
					'name':self.env['ir.sequence'].next_by_code('customer.file.details') or '/',
					'partner_id':self.rec.partner_id.id,
					'logged_user':self.env['res.users'].search([('partner_id','=',self.partner_id.id)]).id,
					'date_today':fields.Date.today(),
					'transfer':self.rec.id,
					'state':'pending',
					'file_details':self.rec.file_details

					})
				self.rec.write({'state': 'waiting',
							'transfer_buddy':self.env['res.users'].search([('partner_id','=',self.partner_id.id)]).id,})



class CustomerFileDetails(models.Model):
	_name = 'customer.file.details'
	_order = 'id desc'

	name = fields.Char()
	partner_id = fields.Many2one('res.partner','Customer Name',required=True)
	date_today = fields.Date('Date',default=fields.Date.today())
	logged_user = fields.Many2one('res.users','Employee/Manager')
	file_location = fields.Char('File Location')
	remarks = fields.Text('Remarks')
	file_details = fields.Char('File Details')
	transfer = fields.Many2one('customer.file.details')
	transfer_buddy = fields.Many2one('res.users')
	state = fields.Selection([('draft','Draft'),('waiting','Waiting'),('pend_cust','For Admin Approval'),('transfer','Transferred'),('pending','Pending'),('accept','Accepted')],default='draft')
	status = fields.Selection([('shown', 'shown'), ('draft', 'draft')], default='draft')

	@api.multi
	def get_notifications(self):
		result = []
		for obj in self:
			result.append({
				'logged':obj.logged_user.name,
				'status': obj.status,
				'id': obj.id,
			})
		return result


	_defaults = {
		'logged_user':lambda obj, cr, uid, ctx=None: uid,
		}


	@api.model
	def create(self, vals):
		result = super(CustomerFileDetails, self).create(vals)
		print "result.nameresult.name", result.name
		if result.name == False:
			result.name = self.env['ir.sequence'].next_by_code('customer.file.details') or '/'
		return result


	@api.multi
	def transfer_document(self):
		view_ref = self.env['ir.model.data'].get_object_reference('hiworth_project_management', 'view_project_transfer_document_wizard')
		view_id = view_ref[1] if view_ref else False
		res = {
		   'type': 'ir.actions.act_window',
		   'name': _('Transfer Document'),
		   'res_model': 'transfer.document',
		   'view_type': 'form',
		   'view_mode': 'form',
		   'view_id': view_id,
		   'target': 'new',
		   'context': {'default_rec':self.id}
	   }

		return res

	@api.multi
	def accept_document(self):
		self.state = 'accept'
		self.transfer.sudo().write({'state': 'transfer'})

	@api.multi
	def approve_file(self):
		self.state = 'transfer'
