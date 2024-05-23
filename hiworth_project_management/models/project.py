from openerp import models, fields, api, _
import dateutil.parser
from datetime import timedelta
AVAILABLE_PRIORITIES = [
	('0', 'Very Low'),
	('1', 'Low'),
	('2', 'Normal'),
	('3', 'High'),
	('4', 'Very High'),
	('5', 'Excellent')
]



class EventEvent(models.Model):
	_inherit = 'event.event'
	_order = 'date_begin desc'

	@api.one
	def button_draft(self):
		self.state = 'initial'
		self.status = 'initial'

	@api.multi
	def finish_task(self):
		self.state = 'completed'
		self.status = 'completed'
		self.date_end = fields.date.today()


	template_id = fields.Many2one('event.event', string="Template")
	is_template = fields.Boolean(string="Is Template")
	number = fields.Char(default='/',readonly=True)
	event_project = fields.Many2one('project.project',store=True)
	project_id = fields.Many2one('project.project',string="Project Name")
	report = fields.Text('Report')
	# user_id = fields.Many2one('res.users','Employee')
	civil_contractor = fields.Many2one('res.partner','Customer')
	reviewer_id = fields.Many2one('res.users','Reviewer')
	project_manager = fields.Many2one('res.users','Project Manager')
	report_time = fields.Datetime('Reporting Time',required=False)
	assigned_date = fields.Date('Assigned Date')
	deadline = fields.Date(string='Deadline')
	issue_id = fields.Many2one('issue.issue',string="Issue Name")

	status = fields.Selection([('initial','Not Completed'),('completed','Completed')],default="initial",string="Status")
	remarks = fields.Text(string='Description')
	status1 = fields.Selection([('shown', 'shown'), ('draft', 'draft')], default='draft')
	date = fields.Date('Date')
	duration=fields.Float('duration')
	current_user = fields.Many2one('res.users',string="User")
	priority = fields.Selection(AVAILABLE_PRIORITIES, 'Priority', select=True)
	update_sel = fields.Selection([('not','Not'),('bw','Bw'),('updated','Updated')],default='not')
	update = fields.Selection([('shown', 'shown'), ('draft', 'draft')], default='draft')
	state = fields.Selection([
			('draft', 'Unconfirmed'),
			('cancel', 'Cancelled'),
			('confirm', 'Confirmed'),
			('done', 'Done'),
			('initial','Not Completed'),
			('completed','Completed')
		], string='Status', default='initial', readonly=True, required=True, copy=False,)
	date_begin = fields.Datetime(string='Start Date', required=False,
		readonly=True, states={'initial': [('readonly', False)]})
	date_end = fields.Datetime(string='End Date', required=False,
		readonly=True, states={'initial': [('readonly', False)]})
	completion_time = fields.Datetime(string='Completion Date',
		readonly=True)


	@api.one
	def button_template(self):
		self.is_template = True

	@api.onchange('template_id')
	def onchange_template_id(self):
		if self.template_id:
			self.issue_id = self.template_id.issue_id.id or False
			self.name = self.template_id.name
			self.project_id = self.template_id.project_id.id or False
			self.project_manager = self.template_id.project_manager.id or False
			self.company_id = self.template_id.company_id.id or False
			self.remarks = self.template_id.remarks
			self.type = self.template_id.type.id
			self.report = self.template_id.report
		

	@api.one
	@api.onchange('issue_id')
	def onchange_issue_id(self):
		if self.issue_id:
			self.name = self.issue_id.name
			self.project_id = self.issue_id.project_id.id or False
			self.remarks = self.issue_id.note

	@api.multi
	def button_evaluate(self):
		pass

	@api.multi
	def send_work_report(self):
		view_ref = self.env['ir.model.data'].get_object_reference('hiworth_project_management', 'view_my_work_report_form')
		view_id = view_ref[1] if view_ref else False
		res = {
		   'type': 'ir.actions.act_window',
		   'name': _('Daily Report'),
		   'res_model': 'my.work.report',
		   'view_type': 'form',
		   'view_mode': 'form',
		   'view_id': view_id,
		   'target': 'current',
		   'context': {'default_req_end':True if self.state == 'completed' else False,'default_report':self.report,'default_project':self.project_id.id,'default_task_id':self.id,'date_end':self.date_end}
	   } 
	 
		return res


	_defaults = {
		
		'reviewer_id': lambda obj, cr, uid, ctx=None: 1,
		'current_user': lambda obj, cr, uid, ctx=None: uid,
		
	}

	@api.onchange('project_id')
	def onchange_project_id(self):
		if self.project_id:
			self.project_manager = self.project_id.user_id.id
			self.civil_contractor = self.project_id.partner_id.id

	@api.onchange('date_end')
	def onchange_date_end(self):
		if self.date_end:
			self.date = dateutil.parser.parse(self.date_end).date() 
			date_end = fields.Datetime.from_string(self.date_end)
			self.report_time = fields.Datetime.to_string(date_end - timedelta(minutes=60))



	@api.model
	def create(self, vals):
		result = super(EventEvent, self).create(vals)
		if result.number == '/':
			result.number = self.env['ir.sequence'].next_by_code('event.event') or '/'
		
		val = {
		'date_today':fields.Datetime.now(),
		'name':result.name,
		'status':result.status,
		'remarks':result.remarks,
		'user_id':result.user_id.id,
		'project_task':result.id
		}
		self.env['job.summary'].create(val)
		return result

	@api.multi
	def write(self, vals):
		result = super(EventEvent, self).write(vals)
		if vals.get('status') and self.env.uid != 1:
			if vals.get('status') == 'completed':
				self.update_sel = 'bw'

		rec = self.env['job.summary'].search([('project_task','=',self.id)])
		if rec:
			rec.write(vals)
		return result


	@api.multi
	@api.depends('name', 'date_begin', 'date_end')
	def name_get(self):
		result = []
		for event in self:
			date_begin = fields.Datetime.from_string(event.date_begin)
			date_end = fields.Datetime.from_string(event.date_end)
			dates = [fields.Date.to_string(fields.Datetime.context_timestamp(event, dt)) for dt in [date_begin, date_end] if dt]
			dates = sorted(set(dates))
			result.append((event.id, '%s' % (event.name)))
		return result


	@api.multi
	def get_notifications(self):
		result = []
		for obj in self:
			result.append({
				'title': obj.name,
				'user':obj.project_manager.name,
				'status': obj.status1,
				'assigned_to':obj.user_id.name,
				'id': obj.id,
				'user_id':obj.user_id.name,
				'update':obj.update,
				'update_sel':obj.update_sel,
				'reviewer_id':obj.reviewer_id.name

			})
		return result



class ProjectProject(models.Model):
	_inherit = 'project.project'
	_order = 'id desc'

	@api.model
	def create(self, vals):
		result = super(ProjectProject, self).create(vals)
		if result['name'] == False: 
			seq = self.env['ir.sequence'].next_by_code('project.project')
			result['name'] = str('PBA/')+str(self.project_category)+str('/')+seq[:3]+str('/1/')+seq[-4:]
		return result


	def set_open(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state': 'open','status_pro':'ongoing'}, context=context)

	def set_done(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state': 'close','status_pro':'completed'}, context=context)

	def set_pending(self, cr, uid, ids, context=None):
		return self.write(cr, uid, ids, {'state': 'pending','status_pro':'pending'}, context=context)


	@api.multi
	def reopen_project(self):
		self.state = 'open'
		self.status_pro = 'ongoing'
		number = self.name[-6]
		if number:
			if number.isdigit():
				number = int(number)
				number = number+1
		self.name = self.name[:-6]+str(number)+self.name[-5:]

	@api.multi
	def name_get(self):
		result = []
		for record in self:
			if record.partner_id.nick_name:
				result.append((record.id,u"%s (%s)" % (record.name, record.partner_id.nick_name)))
			else:
				result.append((record.id,u"%s" % (record.name)))
		return result

	@api.multi
	def add_image(self):
		view_ref = self.env['ir.model.data'].get_object_reference('hiworth_project_management', 'view_ir_attachment_form_view')
		view_id = view_ref[1] if view_ref else False
		res = {
		   'type': 'ir.actions.act_window',
		   'name': _('Add Image'),
		   'res_model': 'ir.attachment',
		   'view_type': 'form',
		   'view_mode': 'form',
		   'view_id': view_id,
		   'target': 'new',
		   'context': {'default_project_image':self.id}
	   }
	 
		return res

	@api.multi
	def get_meeting(self):
		res = {
		   'type': 'ir.actions.act_window',
		   'name': _('Meetings'),
		   'domain':[('project_id','=',self.id)],		   
		   'res_model': 'site.visit.schedule',
		   'view_type': 'form',
		   'view_mode': 'tree,form',
		   'view_id': False,
		   'target': 'current',
	   }
	 
		return res

	@api.multi
	def get_issues(self):
		res = {
		   'type': 'ir.actions.act_window',
		   'name': _('Issues'),
		   'domain':[('project_id','=',self.id)],
		   'res_model': 'issue.issue',
		   'view_type': 'form',
		   'view_mode': 'tree,form',
		   'view_id': False,
		   'target': 'current',
	   }
	 
		return res

	@api.multi
	def get_tasks(self):
		res = {
		   'type': 'ir.actions.act_window',
		   'name': _('Tasks'),
		   'domain':[('project_id','=',self.id)],
		   'res_model': 'event.event',
		   'view_type': 'form',
		   'view_mode': 'tree,form',
		   'view_id': False,
		   'target': 'current',
	   }
	 
		return res

	def get_total_meetings(self):
		meetings = self.env['site.visit.schedule'].search([('project_id','=',self.id)])
		self.total_meetings = len(meetings)

	def get_total_issues(self):
		issues = self.env['issue.issue'].search([('project_id','=',self.id)])
		self.total_issues = len(issues)

	def get_total_task(self):
		tasks = self.env['event.event'].search([('project_id','=',self.id)])
		self.total_task = len(tasks)


	event = fields.One2many('event.event','project_id',string='Tasks')
	no_story = fields.Char('No Of Stories')
	work_report_man = fields.Many2one('res.users')
	work_reports = fields.One2many('work.report','project',string='Approved Work Reports')
	site_image = fields.Many2many('ir.attachment','project_img_rel', 'project_id','attachment_id')
	keywords = fields.Many2many('keywords.tags','keyword_tags_rel','keyword','tags',string="keywords")
	face_direction = fields.Many2one('facing.direction',string="Facing Direction")
	status_pro = fields.Selection([('ongoing','On Going'),('pending','Pending'),('completed','Completed')],default='ongoing')
	project_category = fields.Selection([('Arc','Architecture'),('Str','Structural'),('Intr','Interiors'),('Oth','Other')])
	branch = fields.Many2one('branch.project',string="Branch")
	drawing_sheet = fields.One2many('ir.attachment','drawing_id')
	partner_id = fields.Many2one('res.partner','Awarder')
	site_engineer = fields.Many2one('hr.employee','Site Engineer')
	description = fields.Text('Description')
	tender_id = fields.Many2one('hiworth.tender','Tender')
	expected_start = fields.Date('Expected Start Date')
	expected_end = fields.Date('Expected End Date')
	contractor_id = fields.Many2one('res.company.new', 'Contractor')
	primary_contact = fields.Char(string="Primary Contact Number")
	total_meetings = fields.Float(string="Meetings", compute='get_total_meetings')
	total_issues = fields.Float(string="Issues", compute='get_total_issues')
	total_task = fields.Float(string="Tasks", compute='get_total_task')


class FacingDirection(models.Model):
	_name = 'facing.direction'

	name = fields.Char('Direction')


class KeywordTags(models.Model):
	_name = 'keywords.tags'

	name = fields.Char('Name')

class ResPartner(models.Model):
	_inherit = 'res.partner'

	def get_country_id_customer(self):
		country = self.env['res.country'].search([('code','=','IN')])
		if country:
			if country[0]:
				return country[0]
			
	
	is_cus = fields.Boolean()
	cus_date = fields.Date('Date',default=fields.Date.today())
	my_remarks = fields.Text('Remarks')
	external_user = fields.Boolean('External User', default=False)
	user = fields.Many2one('res.users', 'Assigned to')
	nick_name = fields.Char('Nick Name')
	dob = fields.Date('DOB')
	occupation = fields.Char('Occupation')
	street1 = fields.Char('Street')
	street3 = fields.Char('Post Office')
	city1 = fields.Char('City')
	state_id1 = fields.Many2one('res.country.state')
	country_id = fields.Many2one('res.country',default=get_country_id_customer)
	country_id1 = fields.Many2one('res.country',default=get_country_id_customer)
	zip1 = fields.Char('Zip')
	wife_hus = fields.Char('Wife/Husband')
	dob_wh = fields.Date('DOB')
	children = fields.One2many('children.details','children_id')
	wdng_day = fields.Date('Wedding Anniversary Date')
	# remarks = fields.Text('Remarks')
	res_id1 = fields.Integer()
	current_user = fields.Many2one('res.users')




	
	_defaults = {
		'user': lambda obj, cr, uid, ctx=None: uid,
		}

	@api.onchange("country_id",'country_id1')
	def onchange_country_id_pro(self):
		if self.country_id or self.country_id1:
			ids = []
			
			record = self.env['res.country.state'].search([('country_id','=',self.env['res.country'].search([('code','=','IN')])[0].id)])

			if record:
				for item in record:
					ids.append(item.id)
				return {'domain': {'state_id': [('id', 'in', ids)],
								   'state_id1': [('id', 'in', ids)]}}
		   
			



			

	@api.multi
	def write(self, vals):
		result = super(ResPartner, self).write(vals)
		print "result =============", result
		if self.is_company != True:
			if vals.get('email'):
				rec = self.env['res.users'].search([('partner_id','=',self.id)])
				print "rec===============", rec
				if rec:
					print "aaaaaaaaaaaaaaa"
					rec.write({'login':vals['email']})
		return result


	@api.model
	def create(self, vals):

		group_id = self.env['ir.model.data'].get_object('hiworth_project_management',  'group_user').id
		group_id_contractor = self.env['ir.model.data'].get_object('hiworth_project_management',  'group_contractor').id

		user_id = False
		payable_account = False
		receivable_account = False
		print 'test======================2',vals.get('contractor') ,vals.get('supplier'), vals.get('default_diesel_pump_bool'),  vals.get('customer'),vals.get('is_cus')
		if vals.get('contractor') or vals.get('supplier') or vals.get('default_diesel_pump_bool'):
			user_type = self.env['account.account.type'].search([('name','=','Payable')])
			parent = self.env['account.account'].search([('name','=','Sundry Creditors'),('company_id','=',vals.get('company_id'))])
			temp = 0
			list = []
			code = ""
			for child in parent.child_id:
				temp = int(child.code)
				list.append(temp)    
				if max(list) == 0:
					code = self.parent.code + '001'
				if max(list) != 0:
					code = str(max(list)+1)
			values = {'parent_id': parent.id,
					  'name': vals.get('name'),
					  'code': code,
					  'type': 'payable',
					  'user_type': user_type.id,
					  'reconcile':True,
					  }
			if vals.get('property_account_payable') == False :

				payable_account = self.env['account.account'].create(values)
			
			print 'payable_account======================2',payable_account
		if vals.get('customer'):
			user_type = self.env['account.account.type'].search([('name','=','Receivable')])
			parent = self.env['account.account'].search([('name','=','Sundry Debtors'),('company_id','=',vals.get('company_id'))])
			temp = 0
			list = []
			code = ""
			for child in parent.child_id:
				temp = int(child.code)
				list.append(temp)    
				if max(list) == 0:
					code = self.parent.code + '001'
				if max(list) != 0:
					code = str(max(list)+1)
			values = {'parent_id': parent.id,
					  'name': vals.get('name'),
					  'code': code,
					  'type': 'receivable',
					  'user_type': user_type.id,
					  'reconcile':True,
					  }
			if vals.get('property_account_receivable') == False :
				receivable_account = self.env['account.account'].create(values)
		result = super(ResPartner, self).create(vals)
		if payable_account != False:
			result.write({'property_account_payable':payable_account,'property_account_receivable':payable_account})
		if receivable_account != False:
			result.write({'property_account_receivable':receivable_account,'property_account_payable':receivable_account})

		if result.email and result.customer == True:
			result.is_cus = True
			v = {
			 'active': True,
			 'login': result.email,
			 'company_id': 1,
			 'partner_id': result.id,
			 'groups_id': [(6, 0, [group_id])]
			}
			user_id = self.env['res.users'].sudo().create(v)
		if result.email and result.contractor == True:
			v = {
			 'active': True,
			 'login': result.email,
			 'company_id': 1,
			 'partner_id': result.id,
			 'groups_id': [(6, 0, [group_id_contractor])]
			}
			user_id = self.env['res.users'].sudo().create(v)
		if user_id != False:
			print "user_id===========", user_id
			result.current_user = user_id.id

		print 'sssssssssssssss',result.property_account_payable
		return result




	# @api.model
	# def create(self, vals):

	# 	group_id = self.env['ir.model.data'].get_object('hiworth_project_management',  'group_user').id
	# 	group_id_contractor = self.env['ir.model.data'].get_object('hiworth_project_management',  'group_contractor').id

	# 	user_id = False
	# 	payable_account = False
	# 	receivable_account = False
	# 	print 'test======================2',vals.get('contractor') ,vals.get('supplier')
	# 	if vals.get('contractor') or vals.get('supplier'):
	# 		user_type = self.env['account.account.type'].search([('name','=','Payable')])
	# 		parent = self.env['account.account'].search([('name','=','Sundry Creditors'),('company_id','=',vals.get('company_id'))])
	# 		temp = 0
	# 		list = []
	# 		code = ""
	# 		for child in parent.child_id:
	# 			temp = int(child.code)
	# 			list.append(temp)    
	# 			if max(list) == 0:
	# 				code = self.parent.code + '001'
	# 			if max(list) != 0:
	# 				code = str(max(list)+1)
	# 		values = {'parent_id': parent.id,
	# 				  'name': vals.get('name'),
	# 				  'code': code,
	# 				  'type': 'payable',
	# 				  'user_type': user_type.id,
	# 				  'reconcile':True,
	# 				  }
	# 		payable_account = self.env['account.account'].create(values)
			
	# 		print 'payable_account======================2',payable_account
	# 	if vals.get('customer'):
	# 		user_type = self.env['account.account.type'].search([('name','=','Receivable')])
	# 		parent = self.env['account.account'].search([('name','=','Sundry Debtors'),('company_id','=',vals.get('company_id'))])
	# 		temp = 0
	# 		list = []
	# 		code = ""
	# 		for child in parent.child_id:
	# 			temp = int(child.code)
	# 			list.append(temp)    
	# 			if max(list) == 0:
	# 				code = self.parent.code + '001'
	# 			if max(list) != 0:
	# 				code = str(max(list)+1)
	# 		values = {'parent_id': parent.id,
	# 				  'name': vals.get('name'),
	# 				  'code': code,
	# 				  'type': 'receivable',
	# 				  'user_type': user_type.id,
	# 				  'reconcile':True,
	# 				  }
	# 		receivable_account = self.env['account.account'].create(values)
	# 	result = super(ResPartner, self).create(vals)
	# 	if payable_account != False:
	# 		result.write({'property_account_payable':payable_account})
	# 	if receivable_account != False:
	# 		result.write({'property_account_receivable':receivable_account})

	# 	if result.email and result.customer == True:
	# 		result.is_cus = True
	# 		v = {
	# 		 'active': True,
	# 		 'login': result.email,
	# 		 'company_id': 1,
	# 		 'partner_id': result.id,
	# 		 'groups_id': [(6, 0, [group_id])]
	# 		 # 'create_uid': 1,
	# 		 # 'write_uid': 1,
	# 		 # 'display_groups_suggestions': False,
	# 		 # 'share': False
	# 		}
	# 		user_id = self.env['res.users'].sudo().create(v)
	# 	if result.email and result.contractor == True:
	# 		v = {
	# 		 'active': True,
	# 		 'login': result.email,
	# 		 'company_id': 1,
	# 		 'partner_id': result.id,
	# 		 'groups_id': [(6, 0, [group_id_contractor])]
	# 		 # 'create_uid': 1,
	# 		 # 'write_uid': 1,
	# 		 # 'display_groups_suggestions': False,
	# 		 # 'share': False
	# 		}
	# 		user_id = self.env['res.users'].sudo().create(v)
	# 	if user_id != False:
	# 		print "user_id===========", user_id
	# 		result.current_user = user_id.id

	# 	print 'sssssssssssssss',result.property_account_payable
	# 	return result
	# 	# self.env['res.users'].create({'name':self.name,'login':self.email})
	# 	# result = super(ResPartner, self).create(cr, uid, data, context=context)
	# 	# self.pool.get('res.partner').browse(cr, uid, result, context=context).is_cus = True
	# 	# self.pool.get('res.users').create(cr,uid,{'name':self.name,'email':self.email})
	# 	# return super(ResPartner, self).create(vals)

class ChildrenDetails(models.Model):
	_name = 'children.details'

	children_id = fields.Many2one('res.partner')
	name = fields.Char('Children')
	dob = fields.Date('DOB')


class JobAssignment(models.Model):
	_name = 'job.assignment'
	_order = 'id desc'

	
	name = fields.Char('PBA',readonly=True)
	user_id = fields.Many2one('res.partner')
	address1 = fields.Text('Address')
	contact1 = fields.Char('Contact number of Customer',default="1.")
	contact2 = fields.Char('Contact',default="2.")
	nick_name = fields.Char('Nick Name')
	dob = fields.Date('D.O.B')
	work_type = fields.Char('Type of Work')
	bldng_direction = fields.Char('Facing direction of building')
	area_limit = fields.Char('Initial Area Limit')
	no_stories = fields.Char('No Of Stories')
	assignd_to = fields.Many2one('hr.department','Assigned To')
	location = fields.Many2one('stock.location','Location')
	assignd_by = fields.Many2one('res.users','Assigned By',default=lambda self: self.env.user,readonly=True)
	date_today = fields.Date('Date',default=fields.Date.today)
	tasks_all = fields.One2many('task.entry','project_id')
	tasks_report_all = fields.One2many('task.entry','task_pro')
	my_remarks = fields.Text('Remarks')
	initial_meeting = fields.Date('Expected date of initial meeting')
	final_meeting = fields.Date('Date of Finalisation')
	issuing_submission = fields.Date('Date of issuing Submission File')
	issuing_working = fields.Date('Date of issuing Working File')
	remark1 = fields.Char('Remarks')
	remark2 = fields.Char('Remarks')
	revisions = fields.One2many('rivision.remark','rivision_id')
	project_name = fields.Char('Project Name(Based On Customer Requirement)')
	state = fields.Selection([
			('draft','Draft'),
			('confirm','Confirmed'),
		], string='Status', index=True, readonly=True, default='draft',
		 copy=False)
	site_visit = fields.One2many('site.visit.schedule','pba')
	latitude= fields.Float(string="Latitude",digits=(16,5))
	longitude = fields.Float(string="Longitude",digits=(16,5)) 



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
	def convert_to_project(self):

		view_ref = self.env['ir.model.data'].get_object_reference('hiworth_project_management', 'view_project_manager_charge_form')
		view_id = view_ref[1] if view_ref else False
		res = {
		   'type': 'ir.actions.act_window',
		   'name': _('Manager InCharge'),
		   'res_model': 'manager.charge',
		   'view_type': 'form',
		   'view_mode': 'form',
		   'view_id': view_id,
		   'target': 'new',
		   'context': {'default_rec':self.id}
	   }
	 
		return res
		# self.state = 'confirm'
		# period_obj = self.env['project.project']
		# period_obj.create( {
		#           'name':self.project_name,
		#           'location_id':self.location.id,
		#           'pba_no':self.name,
		#           'partner_id':self.user_id.id,
		#           'no_story':self.no_stories,
		#           'area':self.area_limit,
		#           'direction':self.bldng_direction,
		#           'work_nature':self.work_type
		#       })

	# def convert_to_project(self,cr,uid,ids,context=None):
	#   self.pool('project.project').create(cr,uid,{'name':self.project_name,'location_id':self.location.id,'pba_no':self.name,'partner_id':self.user_id.id})

	@api.onchange('user_id')
	def onchange_user_id(self):
		if self.user_id:
			if self.user_id.mobile:
				self.contact1 = "1."+self.user_id.mobile
			else:
				self.contact1 = '1.'
			if self.user_id.phone:
				self.contact2 = "2."+self.user_id.phone
			else:
				self.contact2 = '2.'
			if self.user_id.street:
				street = self.user_id.street
			else:
				street = ''
			if self.user_id.street2:
				street2 = self.user_id.street
			else:
				street2 = ''
			if self.user_id.city:
				city = self.user_id.city
			else:
				city = ''
			if self.user_id.state_id:
				state_id = self.user_id.state_id.name
			else:
				state_id = ''
			if self.user_id.country_id:
				country_id = self.user_id.country_id.name
			else:
				country_id = ''
			self.address1 = street+'\n'+street2+'\n'+city+'\n'+state_id+'\n'+country_id
			if self.user_id.nick_name:
				self.nick_name = self.user_id.nick_name
			if self.user_id.dob:
				self.dob = self.user_id.dob


	def create(self, cr, uid, vals, context=None):
		if vals.get('name') == None:
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'job.assignment', context=context) or '/'
		order =  super(JobAssignment, self).create(cr, uid, vals, context=context)
		return order

class ManagerCharge(models.Model):
	_name = 'manager.charge'

	manager = fields.Many2one('res.users','Project Manager')
	project_category = fields.Selection([('Arc','Architecture'),('Str','Structural'),('Intr','Interiors'),('Oth','Other')],required=True)
	branch = fields.Many2one('branch.project',string="Branch",required=False)
	rec = fields.Many2one('job.assignment')

	# @api.onchange("manager")
	# def onchange_manager_id(self):
	# 	record = self.env['res.users'].search([('employee_id.employee_type','=','manager')])
	# 	list = []
	# 	for item in record:
	# 		list.append(item.id)

	# 	return {'domain': {'manager': [('id', 'in', list)]}}

	@api.multi
	def confirm_manager(self):
		self.rec.state = 'confirm'
		period_obj = self.env['project.project'] 
		seq = self.env['ir.sequence'].next_by_code('project.project')
		rec = period_obj.create( {
					'name':str('PBA/')+str(self.branch.code)+str('/')+str(self.project_category)+str('/')+seq[:3]+str('/1/')+seq[-4:],
					'location_id':self.rec.location.id,
					'pba_no':self.rec.name,
					'partner_id':self.rec.user_id.id,
					'no_story':self.rec.no_stories,
					'area':self.rec.area_limit,
					'direction':self.rec.bldng_direction,
					'user_id':self.manager.id,
					'work_nature':self.rec.work_type,
					'latitude':self.rec.latitude,
					'longitude':self.rec.longitude,
					'start_date':fields.Date.today(),
					'project_category':self.project_category,
				})
		rec.analytic_account_id.manager_id = self.manager.id


class Rivision(models.Model):
	_name = 'rivision.remark'

	rivision_id = fields.Many2one('job.assignment')
	rivision = fields.Char('Revision')
	remarks = fields.Char('Remarks')


	
class SiteDetails(models.Model):
	_name = 'site.details'

	user_id = fields.Many2one('res.partner')
	location = fields.Many2one('stock.location','Location')
	survey_no = fields.Char('Survey Number')
	ward = fields.Char('Ward')
	north = fields.Char('North')
	east = fields.Char('East')
	south = fields.Char('South')
	west = fields.Char('West')
	deed_no = fields.Many2one('deed.number','Deed No')
	deed_date = fields.Date('Deed Date')
	nearest_build = fields.Many2one('nearest.building','Nearest Building')
	classification = fields.Char('Classification')
	direction = fields.Char('Direction')
	area_limit = fields.Char('Area Limit')
	budget = fields.Char('Budget')
	no_of_stories = fields.Char('No Of stories')
	attachment = fields.Binary('Attachment If Any')
	anyy = fields.Char('Any')
	extend = fields.Char('Extend')
	remarks = fields.Text('Remarks')
	


class ProjectTasks(models.Model):
	_name = 'task.entry'
	_order = 'date_today desc'

	name = fields.Char('Title')
	sl_no = fields.Integer('No')
	task_pro = fields.Integer()
	project_id = fields.Many2one('job.assignment','PBA')
	date_today = fields.Date('Date',default=fields.Date.today())
	status = fields.Selection([('initial','Not Completed'),('completed','Completed')],default="initial",string="Status")
	user_id = fields.Many2one('res.users', 'Assigned to')
	assigned_by = fields.Many2one('res.users', 'Assigned By')
	remarks = fields.Text('Remarks')
	status1 = fields.Selection([('shown', 'shown'), ('draft', 'draft')], default='draft')
	state = fields.Selection([('draft','Draft'),('complete','Completed')],default="draft")

	_defaults = {
		'assigned_by': lambda obj, cr, uid, ctx=None: uid,
		}

	
	@api.multi
	def complete_task(self):
		self.state = 'complete'
		self.status = 'completed'


	@api.onchange("user_id")
	def onchange_user_id(self):
		record = self.env['res.partner'].search([('is_cus','!=',True)])
		ids = []
		list = []
		for item in record:
			if item.contractor == False:
				ids.append(item.id)

		for idss in ids:
			rec = self.env['res.users'].search([('partner_id','=',idss)])
			list.append(rec.id)

		return {'domain': {'user_id': [('id', 'in', list)]}}

	@api.model
	def create(self, vals):
		result = super(ProjectTasks, self).create(vals)
		val = {
		'date_today':result.date_today,
		'name':result.name,
		'status':result.status,
		'remarks':result.remarks,
		'user_id':result.user_id.id,
		'task_entry':result.id
		}
		self.env['job.summary'].create(val)
		return result

	@api.multi
	def write(self, vals):
		result = super(ProjectTasks, self).write(vals)
		rec = self.env['job.summary'].search([('task_entry','=',self.id)])
		if rec:
			rec.write(vals)
		return result

	@api.multi
	def get_notifications(self):
		result = []
		for obj in self:
			result.append({
				'title': obj.name,
				'user':obj.assigned_by.name,
				'status': obj.status1,
				'assigned_to':obj.user_id.name,
				'id': obj.id,
				'id1':obj.assigned_by.id
			})
		return result



class NearestBuilding(models.Model):
	_name = 'nearest.building'

	name = fields.Char('Building Name')



class DeedNumber(models.Model):
	_name = 'deed.number'

	name = fields.Char('Number')



class SiteVisit(models.Model):
	_name = 'site.visit'

	site_visit = fields.One2many('site.visit.schedule','site_id')
	user = fields.Many2one('res.users', 'Assigned to')
	pba = fields.Many2one('job.assignment','Related PBA')

	
	
	_defaults = {
		'user': lambda obj, cr, uid, ctx=None: uid,
		}


	# @api.onchange("pba")
	# def onchange_related_pba(self):
	#   ids = []
	#   record = self.env['task.entry'].search([('assigned_to','=',self.visit_by.id)])
	#   if record:
	#       for item in record:
	#           ids.append(item.id)
	#       return {'domain': {'pba': [('id', 'in', ids)]}}

class SiteVisitSchedule(models.Model):
	_name = 'site.visit.schedule'
	_order = 'date_today desc'

	template_id = fields.Many2one('site.visit.schedule', string="Template")
	is_template = fields.Boolean(string="Is Template")	
	name = fields.Char(string='Name of Meeting')
	date_today = fields.Date(string='Date of Visit',default=fields.Date.today())
	time = fields.Float(string="Time")
	member_ids = fields.Many2many('res.users',string="Members Present")
	mom = fields.Text(string="Meeting Minutes")
	state = fields.Selection([('draft','Draft'),('complete','Completed')],default="draft")
	project_id = fields.Many2one('project.project', string="Project")

	site_id = fields.Many2one('site.visit',store=True)
	assigned = fields.Many2one('res.users','Assigned By')
	visit_by = fields.Many2one('res.users','Assigned To')
	location = fields.Many2one('stock.location','Location Of Site')
	remarks = fields.Text('Remarks')
	pba = fields.Many2one('job.assignment','Related PBA',)
	status = fields.Selection([
			('notvisited','Not Visited'),
			('visited','Visited'),
		], string='Status', default='notvisited',
		 copy=False)
	status1 = fields.Selection([('shown', 'shown'), ('draft', 'draft')], default='draft')

	_defaults = {
		'assigned': lambda obj, cr, uid, ctx=None: uid,
		}

	@api.multi
	def complete_task(self):
		self.state = 'complete'
		self.status = 'visited'

	@api.one
	def button_template(self):
		self.is_template = True

	@api.onchange('template_id')
	def onchange_template_id(self):
		if self.template_id:
			ids = []
			for val in self.template_id.member_ids:
				ids.append(val.id)
			print '-------------ids---------------',ids
			self.name = self.template_id.name
			self.time = self.template_id.time
			self.project_id = self.template_id.project_id.id
			self.member_ids = [(6,0,ids)]
			self.mom = self.template_id.mom

	# @api.multi
	# def get_notifications(self):
	# 	result = []
	# 	for obj in self:
	# 		result.append({
	# 			'title': obj.location.name,
	# 			'visit_by': obj.visit_by.name,
	# 			'user':obj.assigned.name,
	# 			'status1': obj.status1,
	# 			'id': obj.id,
	# 		})
	# 	return result
	

	

	
	# 		