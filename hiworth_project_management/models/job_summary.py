from openerp import models, fields, api

class JobSummary(models.Model):
	_name = 'job.summary'

	name = fields.Char('Description')
	date_today = fields.Datetime('Date')
	status = fields.Selection([('initial','Not Completed'),('completed','Completed')],default="initial",string="Status")
	remarks = fields.Text('Remarks')
	user_id = fields.Many2one('res.users', 'Assigned To')
	task_entry = fields.Many2one('task.entry',store=True)
	project_task = fields.Many2one('event.event',store=True)

class JobSummaryWizard(models.Model):
	_name = 'job.summary.wizard'
	_rec_name = 'employee'

	date_from = fields.Datetime('Period From')
	date_to = fields.Datetime('Period To')
	employee = fields.Many2one('res.users','Employee')

	@api.multi
	def confirm_date(self):
		if self.date_from == False and self.date_to == False:
			if not self.employee:
				return {
					'name': 'Job Summary',
					'view_type': 'form',
					'view_mode': 'tree,form',
					'res_model': 'event.event',
					'domain': [],
					'target': 'current',
					'type': 'ir.actions.act_window',
					'context': {},

				}
			else:
				return {
					'name': 'Job Summary',
					'view_type': 'form',
					'view_mode': 'tree,form',
					'res_model': 'event.event',
					'domain': [('user_id','=',self.employee.id)],
					'target': 'current',
					'type': 'ir.actions.act_window',
					'context': {},

				}

		if self.date_from and self.date_to:
			list = []
			recs = self.env['event.event'].search([('date_begin','>=',self.date_from),('date_begin','<=',self.date_to)])
			if not self.employee:
				for rec in recs:
					list.append(rec.id)
			else:
				recs1 = self.env['event.event'].search([('date_begin','>=',self.date_from),('date_begin','<=',self.date_to),('user_id','=',self.employee.id)])
				for lines in recs1:
					list.append(lines.id)
			return {
				'name': 'Job Summary',
				'view_type': 'form',
				'view_mode': 'tree,form',
				'res_model': 'event.event',
				'domain': [('id','in',list)],
				'target': 'current',
				'type': 'ir.actions.act_window',
				'context': {},

			}




class HrEmployee(models.Model):
	_inherit = 'hr.employee'

	@api.multi
	def write(self, vals):
		result = super(HrEmployee, self).write(vals)
		rec = self.env['res.users'].search([('id','=',self.user_id.id)])
		if rec:
			if rec.partner_id:
				if vals.get('birthday'):
					rec.partner_id.dob = vals.get('birthday')
				if vals.get('wedding_anniversary'):
					rec.partner_id.wdng_day = vals.get('wedding_anniversary')
				if vals.get('work_email'):
					rec.login = vals.get('work_email')
					rec.partner_id.email = vals.get('work_email')

		return result


	@api.model
	def create(self, vals):
		result = super(HrEmployee, self).create(vals)
		group_id_employee = self.env['ir.model.data'].get_object('hiworth_project_management',  'group_employee').id
		group_id_manager = self.env['ir.model.data'].get_object('hiworth_project_management',  'group_manager').id
		group_id_man = self.env['ir.model.data'].get_object('project', 'group_project_manager').id
	   
		if result.work_email and result.employee_type == 'manager':
			v = {
			 'active': True,
			 'name': result.name,
			 'login': result.work_email,
			 'company_id': 1,
			 # 'partner_id': result.id,
			 'employee_id':result.id,
			 'groups_id': [(6, 0, [group_id_manager,group_id_man])]
			
			}
			user_id1 = self.env['res.users'].sudo().create(v)
			result.user_id = user_id1.id

			if result.birthday:
				user_id1.partner_id.dob = result.birthday
			if result.wedding_anniversary:
				user_id1.partner_id.wdng_day = result.wedding_anniversary

		if result.work_email and result.employee_type == 'employee':
			u = {
			 'active': True,
			 'name': result.name,
			 'login': result.work_email,
			 'company_id': 1,
			 # 'partner_id': result.id,
			 'employee_id':result.id,
			 'groups_id': [(6, 0, [group_id_employee])]
			
			}
			user_id2 = self.env['res.users'].sudo().create(u)
			result.user_id = user_id2.id

			if result.birthday:
				user_id2.partner_id.dob = result.birthday
			if result.wedding_anniversary:
				user_id2.partner_id.wdng_day = result.wedding_anniversary
		

		return result
