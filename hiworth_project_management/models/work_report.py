from openerp import models, fields, api, _

class WorkReport(models.Model):
	_name = 'work.report'

	number = fields.Many2one('event.event','Task Number')
	to_ids = fields.Many2many('res.users',string="To")
	from_id = fields.Many2one('res.users',string="From")
	report = fields.Text('Report')
	notes = fields.Text('Notes')
	date_today = fields.Datetime('Date',default=fields.Datetime.now())
	user_id = fields.Many2one('res.users','User')
	customer_id = fields.Many2one('res.users','Customer')
	project = fields.Many2one('project.project','Project')


	_defaults = {
		'user_id':lambda obj, cr, uid, ctx=None: uid,
		}



class MyWorkReport(models.Model):
	_name = 'my.work.report'
	_order = 'id desc'

	
	project = fields.Many2one('project.project','Project', store=True)
	customer_nick = fields.Char('Customer Nick Name',related="project.nick_name",readonly=True)
	to_id = fields.Many2one('res.users',string="To", readonly=True)
	from_id = fields.Many2one('res.users',string="From")
	task_id = fields.Many2one('event.event','Task')
	date_end = fields.Datetime('Default End Date',store=True)
	normal_end = fields.Datetime('End Date')
	req_end = fields.Boolean(default=False)
	report = fields.Text('Report')
	notes = fields.Text('Notes')
	date_today = fields.Datetime('Date',default=fields.Datetime.now())
	user_id = fields.Many2one('res.users','Send By',readonly=True)
	state = fields.Selection([('draft','Draft'),('send','Send'),('sent','Approved')],default="draft")
	sent_report = fields.Many2one('res.users','Send Report')
	status = fields.Selection([('shown', 'shown'), ('draft', 'draft')], default='draft')
	status_admin = fields.Selection([('shown', 'shown'), ('draft', 'draft')], default='draft')
	status_sent = fields.Selection([('shown', 'shown'), ('draft', 'draft')], default='draft')

	@api.model
	def create(self, vals):
		print "vals=====================", vals
		if vals.get('task_id'):
			vals['date_end'] = self.env['event.event'].search([('id','=',vals.get('task_id'))]).date_end
			print "dateend==========", vals['date_end'] 
			vals['project'] = self.env['event.event'].search([('id','=',vals.get('task_id'))]).project_id.id
		return super(MyWorkReport, self).create(vals)



	@api.onchange('task_id')
	def onchange_task_id(self):
		if self.task_id:
			self.date_end = self.task_id.date_end
			self.project = self.task_id.project_id.id


	@api.multi
	def get_notifications(self):
		result = []
		for obj in self:
			result.append({
				'sent_report':obj.sent_report.name,
				'to_id':obj.to_id.name,
				'manager':obj.project.user_id.name,
				'status': obj.status,
				'status_admin': obj.status_admin,
				'status_sent': obj.status_sent,
				'id': obj.id,
			})
		return result


	@api.multi
	def send_report_user(self):
		view_ref = self.env['ir.model.data'].get_object_reference('hiworth_project_management', 'view_project_send_document_wizard')
		view_id = view_ref[1] if view_ref else False
		res = {
		   'type': 'ir.actions.act_window',
		   'name': _('Send Report'),
		   'res_model': 'transfer.document',
		   'view_type': 'form',
		   'view_mode': 'form',
		   'view_id': view_id,
		   'target': 'new',
		   'context': {'default_recs':self.id}
	   }

		return res


	_defaults = {
		'user_id':lambda obj, cr, uid, ctx=None: uid,
		'to_id' :lambda obj, cr, uid, ctx=None: 1, 
		}


	@api.multi
	def send_report(self):
		if self.normal_end:
			self.task_id.completion_time = self.normal_end
		if self.project:
			self.state = 'sent'
			rec = self.env['res.users'].search([('partner_id','=',self.project.partner_id.id)])
			self.env['work.report'].sudo().create({'date_today':self.date_today,
											'project':self.project.id,
											'customer_id':rec.id,
											'report':self.report,
											'notes':self.notes,
											'user_id':self.user_id.id})




