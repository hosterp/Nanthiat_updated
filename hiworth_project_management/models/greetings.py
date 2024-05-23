from openerp import models, fields, api
import datetime
from lxml import etree
import math
import pytz
import threading
import urlparse

from openerp.osv import osv
from datetime import datetime, timedelta
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp import http
from openerp.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT


class Greetings(models.Model):
	_name = 'greetings.prime'

	name = fields.Char('Greetings Name',required=True)
	date_greet = fields.Date('Greetings Date',required=True)


	def _cron_special_day_reminder(self, cr, uid, context=None):
		su_id =self.pool.get('res.partner').browse(cr, uid, SUPERUSER_ID)
		partners1 = self.pool.get('res.partner')
		partners = partners1.search(cr, uid, (), context=None)
		greetings = self.search(cr, uid, (), context=None)
		for greeting in self.browse(cr, uid, greetings, context=None):
			if greeting.date_greet != False:
				greet_day = datetime.strptime(greeting.date_greet,'%Y-%m-%d').date()
				today =datetime.now().date()
				if greet_day.month == today.month:
					if greet_day.day == today.day:
						for partner_obj in partners:
							partner = self.pool.get('res.partner').browse(cr,uid,partner_obj,context=None)
							if partner.email:
								template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid,
																	  'hiworth_project_management',
																	  'email_template_edi_special_day_reminder')[1]
								email_template_obj = self.pool.get('email.template')
								if template_id:
									values = email_template_obj.generate_email(cr, uid,template_id, partner.id, context=context)
									values['email_from'] = su_id.email
									values['email_to'] = partner.email
									values['res_id'] = False
									if not values['subject']:
										values['subject'] = str(greeting.name)+' '+str('Greetings')
									mail_mail_obj = self.pool.get('mail.mail')
									msg_id = mail_mail_obj.create(cr, SUPERUSER_ID,values)
									if msg_id:
										print "msg_id====================", msg_id
										mail_mail_obj.send(cr, SUPERUSER_ID,[msg_id])

		return True

# class Feedback(models.Model):
# 	_name = 'feedback.prime'

# 	name = fields.Char('Name')


# 	@api.multi
# 	def _cron_feedback_reminder(self):
# 		su_id =self.env['res.partner'].search([('id','=',SUPERUSER_ID)])
# 		partners = self.env['res.partner'].search([])
# 		for partner_obj in partners:
# 			if partner.email:
# 				share = self.env['share.wizard'].create({
# 									'user_type':'emails',
# 									'new_users':partner.email,
# 									'name':'Customer Feedback',
# 									'accessmode':'readwrite',
# 									'action_id': 658
# 				})

# 				share.go_step_2()
# 				user_feedback = self.env['res.users'].search([('name','=',(partner.email).upper()),('login','=',partner.email)])
# 				if user_feedback:
# 					self.env['feedback.hornbill'].sudo().create({'name':self.partner_id.name})
			
# 				template_id = self.env['ir.model.data'].get_object_reference(
# 													  'hiworth_project_management',
# 													  'email_template_edi_special_day_reminder')[1]
# 				email_template_obj = self.pool.get('email.template')
# 				if template_id:
# 					values = email_template_obj.generate_email(cr, uid,template_id, partner.id, context=context)
# 					values['email_from'] = su_id.email
# 					values['email_to'] = partner.email
# 					values['res_id'] = False
# 					if not values['subject']:
# 						values['subject'] = str(greeting.name)+' '+str('Greetings')
# 					mail_mail_obj = self.pool.get('mail.mail')
# 					msg_id = mail_mail_obj.create(cr, SUPERUSER_ID,values)
# 					if msg_id:
# 						print "msg_id====================", msg_id
# 						mail_mail_obj.send(cr, SUPERUSER_ID,[msg_id])

# 		return True
	

