from openerp import models, fields, api,_

class ProjectProject(models.Model):
	_inherit = 'project.project'

	pba_no = fields.Char('Project Number')
	client_id = fields.Char('Client Id')
	work_nature = fields.Char('Nature Of Work')
	building_nature = fields.Char('Nature Of Building')
	permit_authority = fields.Char('Permitting Authority')
	permit_no = fields.Char('Permit Number')
	permit_from = fields.Date('Permit Validity')
	permit_to = fields.Date('Permit To')
	direction = fields.Char('Direction')
	area = fields.Char('Area Of Building')
	area_plot = fields.Float('Area Of Plot')
	survey_no = fields.Char('Survey Number')
	extend = fields.Char('Extend')
	deed_no = fields.Char('Deed Number')
	ward_no = fields.Char('Ward Number')
	no_story = fields.Char('No Of Stories')
	my_remarks = fields.Text('Remarks')
	external_user = fields.Boolean('External User', default=False)
	user = fields.Many2one('res.users', 'Assigned to')
	nick_name = fields.Char('Nick Name',related="partner_id.nick_name")
	dob = fields.Date('DOB',related="partner_id.dob")
	occupation = fields.Char('Occupation',related="partner_id.occupation")
	street1 = fields.Char('Street',related="partner_id.street1")
	street3 = fields.Char('Post Office',related="partner_id.street3")
	city1 = fields.Char('City',related="partner_id.city1")
	state_id1 = fields.Many2one('res.country.state',related="partner_id.state_id1")
	country_id1 = fields.Many2one('res.country',related="partner_id.country_id1")
	zip1 = fields.Char('Zip',related="partner_id.zip1")
	wife_hus = fields.Char('Wife/Husband',related="partner_id.wife_hus")
	dob_wh = fields.Date('DOB',related="partner_id.dob_wh")
	children = fields.One2many('children.details','children_id')
	wdng_day = fields.Date('Wedding Anniversary Date',related="partner_id.wdng_day")
	street = fields.Char('Street',related="partner_id.street")
	street2 = fields.Char('Post Office',related="partner_id.street2")
	city = fields.Char('City',related="partner_id.city")
	state_id = fields.Many2one('res.country.state')
	country_id = fields.Many2one('res.country',related="partner_id.country_id")
	zip = fields.Char('Zip')
	email = fields.Char(related="partner_id.email")
	phone= fields.Char(related="partner_id.phone")
	mobile = fields.Char(related="partner_id.mobile")
	village = fields.Char('Name Of Village')
	taluk = fields.Char('Name Of Taluk')
	district = fields.Char('Name Of District')
	building_no = fields.Char('Building Number')
	local_body = fields.Selection([('panchayathu','PANCHAYATHU'),('muncipality','MUNCIPALITY'),('corporation','CORPORATION')],string="Local Body")
	latitude = fields.Float('latitude',digits=(16,5))
	longitude = fields.Float('longitude',digits=(16,5))
	daily_statement_ids = fields.One2many('partner.daily.statement','project_id')
	site_visit_ids = fields.One2many('site.visit.schedule', 'project_id', string="Site Meetings")

	north = fields.Char('North')
	east = fields.Char('East')
	west = fields.Char('West')
	south = fields.Char('South')

	inbox_one2many = fields.One2many('project.customer.inbox', 'project_id', string='Inbox')
	sent_one2many = fields.One2many('project.customer.sent', 'project_sent_id', string='Sent Messages')
	issue_ids = fields.One2many('issue.issue','project_id')
	attachment_ids = fields.One2many('attachment.attachment','project_id')

	project_details = fields.Selection([
			('client','Client Details'),
			('project','Project Details'),
			('office','Office Management'),
			('site','Site Management'),
			('accounts','Accounts'),
			('messaging','Messaging'),
		], string='Details')

	@api.multi
	def show_google_map(self):
		myurl='https://www.google.co.in/maps/@{},{},15z'.format(self.latitude,self.longitude),
		return {
				'name':"google",

				'type':'ir.actions.act_url',
				
				'target':'new',
				'url':myurl

		}



	@api.multi
	def open_wizard_project_details(self):
		# self.bool_msg = True
		# self.state = 'pending'
		# ids = self.from_id.id
		view_ref = self.env['ir.model.data'].get_object_reference('hiworth_project_management', 'form_project_wizard_prime')
		view_id = view_ref[1] if view_ref else False
		project = self.env['project.project'].search([('partner_id','=', self.partner_id.id),('pba_no','=',self.pba_no)])
		res = {
		   'type': 'ir.actions.act_window',
		   'name': _('Details'),
		   'res_model': 'project.project',
		   'view_type': 'form',
		   'view_mode': 'form',
		   'view_id': view_id,
		   'target': 'new',
		   'res_id': project.id,
		   'context': {'default_partner_id': self.partner_id.id,'default_name': self.name}
	   }
	 
		return res


	@api.onchange('project_details')
	def onchange_customer_message(self):
		if self.project_details == 'messaging':
			inbox_list=[]
			sent_list=[]
			inbox_id = self.env['im_chat.message.req'].search([('to_id','=', self.env['res.users'].search([('partner_id','=',self.partner_id.id)])[0].id)])
			for inbox in inbox_id:
				inbox_list.append((0, False, {'message':inbox.message,'from_id':inbox.from_id,
					'date':inbox.date_today,'to_id':inbox.to_id}))
			self.inbox_one2many = inbox_list

			sent_id = self.env['im_chat.message.req'].search([('sent','=',False),('from_id','=', self.env['res.users'].search([('partner_id','=',self.partner_id.id)])[0].id)])
			for sent in sent_id:
				sent_list.append((0, False, {'message':sent.message,
					'date':sent.date_today,'from_id':sent.from_id,'to_id':sent.to_id}))
			self.sent_one2many = sent_list


class ProjectInbox(models.Model):
	_name = 'project.customer.inbox'

	date = fields.Datetime('Date')
	project_id = fields.Many2one('project.project')
	reply = fields.Text('Reply')
	message = fields.Text('Message')
	from_id = fields.Many2one('res.users','From')
	to_id = fields.Many2one('res.users','To')


class ProjectInbox(models.Model):
	_name = 'project.customer.sent'

	project_sent_id = fields.Many2one('project.project')
	date = fields.Datetime('Date')
	message = fields.Text('Message')
	reply = fields.Text('Reply')
	from_id = fields.Many2one('res.users','From')
	to_id = fields.Many2one('res.users','To')

class Issue(models.Model):
	_name = 'issue.issue'

	template_id = fields.Many2one('issue.issue', string="Template")
	is_template = fields.Boolean(string="Is Template")
	date = fields.Date(string="Date", default=fields.Date.today())
	name = fields.Char(string="Issue Name")
	type_id = fields.Many2one('event.type', string="Type of Task")
	project_id = fields.Many2one('project.project', string="Project")
	deadline = fields.Date(string="Deadline")
	note = fields.Text(string="Description")
	reviewer_id = fields.Many2one('res.users', string="Reviewer")
	user_id = fields.Many2one('res.users', string="Assigned By", default=lambda self: self.env.user)
	assigned_to = fields.Many2one('res.users', string="Assigned To")
	state = fields.Selection([('initial','Not Completed'),('completed','Completed')],default="initial",string="Status")

	@api.one
	def button_finish(self):
		self.state = 'completed'

	@api.one
	def button_template(self):
		self.is_template = True

	@api.onchange('template_id')
	def onchange_template_id(self):
		if self.template_id:
			self.name = self.template_id.name
			self.type_id = self.template_id.type_id.id or False
			self.project_id = self.template_id.project_id.id or False
			self.deadline = self.template_id.deadline
			self.note = self.template_id.note
			self.reviewer_id = self.template_id.reviewer_id.id or False
			self.assigned_to = self.template_id.assigned_to.id or False

class Attachment(models.Model):
	_name = 'attachment.attachment'
	
	project_id = fields.Many2one('project.project', string="Project")
	
	attach = fields.Binary(string="Attachment")
	name = fields.Char(string="Description")