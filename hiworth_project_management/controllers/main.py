import openerp
import openerp.http as http
from openerp.http import request


# class my_api_class(openerp.http.Controller):

# 	@http.route("/get_partner/", auth='none')
# 	def get_partner(self,name):
# 		print "pppppppppppppppppppppppppppppp==========================="
# 		print "JULY CATHARINE CHACKO"
# 		if request.httprequest.method=='GET':
# 			partner_obj = request.env['res.partner']
# 			partner_ids_list=partner_obj.search(request.cr,1,[('name','=',name)])
# 			return str(partner_ids_list)
# 		return str('NOT A GET REQUEST')

# 	@http.route("/insert_partner_data/", auth='none')
# 	def create_partner(self,**vals):
# 		# import ipdb;ipdb.set_trace()
# 		partner_obj = request.env['res.partner']
# 		if request.httprequest.method=='POST' :
# 			header=request.httprequest.headers
# 			partner_ids_list=partner_obj.create(request.cr,1,**vals)
# 			return str(partner_ids_list)


# class PopupController(openerp.http.Controller):

    # @http.route('/hiworth_project_management/notify_leave', type='json', auth="none")
    # def notify_leave(self):
    #     user_id = request.session.get('uid')
    #     # print "user_id .............................", user_id
    #     return request.env['hr.holidays'].sudo().search(
    #         [('admin', '=', user_id), ('status', '!=', 'shown'),('type','=','remove'),('state','=','confirm')]
    #     ).get_notifications()

    # @http.route('/hiworth_project_management/notify_leave_ack', type='json', auth="none")
    # def notify_leave_ack(self, notif_id, type='json'):
    #     notif_obj = request.env['hr.holidays'].sudo().browse([notif_id])
    #     if notif_obj:
    #         notif_obj.status = 'shown'

    # @http.route('/hiworth_project_management/notify_work_report_admin', type='json', auth="none")
    # def notify_work_report_admin(self):
    #     user_id = request.session.get('uid')
    #     # print "user_id .............................", user_id
    #     return request.env['my.work.report'].sudo().search(
    #         [('to_id', '=', user_id), ('status_admin', '!=', 'shown')]
    #     ).get_notifications()

    # @http.route('/hiworth_project_management/notify_work_report_admin_ack', type='json', auth="none")
    # def notify_work_report_admin_ack(self, notif_id, type='json'):
    #     notif_obj = request.env['my.work.report'].sudo().browse([notif_id])
    #     if notif_obj:
    #         notif_obj.status_admin = 'shown'

    # @http.route('/hiworth_project_management/notify_work_report_manager', type='json', auth="none")
    # def notify_work_report_manager(self):
    #     user_id = request.session.get('uid')
    #     # print "user_id .............................", user_id
    #     return request.env['my.work.report'].sudo().search(
    #         [('project.user_id', '=', user_id), ('status', '!=', 'shown')]
    #     ).get_notifications()

    # @http.route('/hiworth_project_management/notify_work_report_man_ack', type='json', auth="none")
    # def notify_work_report_man_ack(self, notif_id, type='json'):
    #     notif_obj = request.env['my.work.report'].sudo().browse([notif_id])
    #     if notif_obj:
    #         notif_obj.status = 'shown'

    # @http.route('/hiworth_project_management/notify_work_report_sent', type='json', auth="none")
    # def notify_work_report_sent(self):
    #     user_id = request.session.get('uid')
        # print "user_id .............................", user_id
    #     return request.env['my.work.report'].sudo().search(
    #         [('sent_report', '=', user_id), ('status_sent', '!=', 'shown')]
    #     ).get_notifications()

    # @http.route('/hiworth_project_management/notify_work_report_sent_ack', type='json', auth="none")
    # def notify_work_report_sent_ack(self, notif_id, type='json'):
    #     notif_obj = request.env['my.work.report'].sudo().browse([notif_id])
    #     if notif_obj:
    #         notif_obj.status_sent = 'shown'

    # @http.route('/hiworth_project_management/notify_file_cust', type='json', auth="none")
    # def notify_file_cust(self):
    #     user_id = request.session.get('uid')
        # print "user_id .............................", user_id
        # return request.env['customer.file.details'].sudo().search(
        #     [('logged_user', '=', user_id), ('status', '!=', 'shown'),('state','=','pending')]
        # ).get_notifications()

    # @http.route('/hiworth_project_management/notify_file_cust_ack', type='json', auth="none")
    # def notify_file_cust_ack(self, notif_id, type='json'):
    #     notif_obj = request.env['customer.file.details'].sudo().browse([notif_id])
    #     if notif_obj:
    #         notif_obj.status = 'shown'

    # @http.route('/hiworth_project_management/notify', type='json', auth="none")
    # def notify(self):
    #     user_id = request.session.get('uid')
        # print "user_id .............................", user_id
    #     return request.env['task.entry'].sudo().search(
    #         [('user_id', '=', user_id), ('status1', '!=', 'shown')]
    #     ).get_notifications()

    # @http.route('/hiworth_project_management/notify_ack', type='json', auth="none")
    # def notify_ack(self, notif_id, type='json'):
    #     notif_obj = request.env['task.entry'].sudo().browse([notif_id])
    #     if notif_obj:
    #         notif_obj.status1 = 'shown'

    # @http.route('/hiworth_project_management/notify_msg', type='json', auth="none")
    # def notify_msg(self):
    #     user_id = request.session.get('uid')
        # print "user_id .............................", user_id
    #     return request.env['im_chat.message.req'].sudo().search(
    #         [('cc_id', '=', user_id), ('status', '!=', 'shown'),('to_id.partner_id.customer', '!=', True)]
    #     ).get_notifications()

    # @http.route('/hiworth_project_management/notify_msg_cust', type='json', auth="none")
    # def notify_msg_cust(self):
    #     user_id = request.session.get('uid')
        # print "user_id .............................", user_id
    #     return request.env['im_chat.message.req'].sudo().search(
    #         [('cc_id', '=', user_id), ('status1', '!=', 'shown'),('state','=','approved'),('to_id.partner_id.customer', '=', True),('require','=',True)]
    #     ).get_notifications()

    # @http.route('/hiworth_project_management/notify_msg_adm', type='json', auth="none")
    # def notify_msg_adm(self):
    # 	user_id = request.session.get('uid')
    #     return request.env['im_chat.message.req'].sudo().search(
    #         [('admin','=',user_id),('require','=',False), ('status', '=', 'shown'),('state','=','pending')]
    #     ).get_notifications()

    # @http.route('/hiworth_project_management/notify_ack_msg', type='json', auth="none")
    # def notify_ack_msg(self, notif_id, type='json'):
    #     notif_obj = request.env['im_chat.message.req'].sudo().browse([notif_id])
    #     if notif_obj:
    #         notif_obj.status = 'shown'

    # @http.route('/hiworth_project_management/notify_ack_msg_cust', type='json', auth="none")
    # def notify_ack_msg_cust(self, notif_id, type='json'):
    #     notif_obj = request.env['im_chat.message.req'].sudo().browse([notif_id])
    #     if notif_obj:
    #         notif_obj.status1 = 'shown'
    #         notif_obj.status = 'shown'

			# site visit schedule

    # @http.route('/hiworth_project_management/notify_site', type='json', auth="none")
    # def notify_site(self):
    #     user_id = request.session.get('uid')
        # print "user_id .............................", user_id
        # return request.env['site.visit.schedule'].sudo().search(
        #     [('visit_by', '=', user_id), ('status1', '!=', 'shown')]
        # ).get_notifications()

    # @http.route('/hiworth_project_management/notify_ack_site', type='json', auth="none")
    # def notify_ack_site(self, notif_id, type='json'):
    #     notif_obj = request.env['site.visit.schedule'].sudo().browse([notif_id])
    #     if notif_obj:
    #         notif_obj.status1 = 'shown'

    # @http.route('/hiworth_project_management/notify_general', type='json', auth="none")
    # def notify_general(self):
    #     user_id = request.session.get('uid')
        # print "user_id .............................", user_id
    #     return request.env['general.message'].sudo().search(
    #         [('to_id', '=', user_id), ('status', '!=', 'shown')]
    #     ).get_notifications()

    # @http.route('/hiworth_project_management/notify_ack_general', type='json', auth="none")
    # def notify_ack_general(self, notif_id, type='json'):
    #     notif_obj = request.env['general.message'].sudo().browse([notif_id])
    #     if notif_obj:
    #         notif_obj.status = 'shown'

    # @http.route('/hiworth_project_management/notify_task_message', type='json', auth="none")
    # def notify_task_message(self):
    #     user_id = request.session.get('uid')
        # print "user_id .............................", user_id
    #     return request.env['event.event'].sudo().search(
    #         [('user_id', '=', user_id), ('status1', '!=', 'shown')]
    #     ).get_notifications()

    # @http.route('/hiworth_project_management/notify_ack_task_message', type='json', auth="none")
    # def notify_ack_task_message(self, notif_id, type='json'):
    #     notif_obj = request.env['event.event'].sudo().browse([notif_id])
    #     if notif_obj:
    #         notif_obj.status1 = 'shown'

    # @http.route('/hiworth_project_management/notify_task_adm', type='json', auth="none")
    # def notify_task_adm(self):
    #     user_id = request.session.get('uid')
    #     return request.env['task.message'].sudo().search(
    #         [('admin','=',user_id), ('status', '!=', 'shown')]
    #     ).get_notifications()

    # @http.route('/hiworth_project_management/notify_ack_task', type='json', auth="none")
    # def notify_ack_task(self, notif_id, type='json'):
    #     notif_obj = request.env['task.message'].sudo().browse([notif_id])
    #     if notif_obj:
    #         notif_obj.status = 'shown'




    # @http.route('/hiworth_project_management/notify_approved_msg', type='json', auth="none")
    # def notify_approved_msg(self):
    #     user_id = request.session.get('uid')
    #     return request.env['im_chat.message.req'].sudo().search(
    #         [('from_id','=',user_id),('to_id.partner_id.customer','=',True), ('state', '=', 'approved'),('bool_msg','=',True),('message_type','=','requirement'),('req_nofify','=','draft')]
    #     ).get_notifications()

    # @http.route('/hiworth_project_management/notify_ack_approved_msg', type='json', auth="none")
    # def notify_ack_approved_msg(self, notif_id, type='json'):
    #     notif_obj = request.env['im_chat.message.req'].sudo().browse([notif_id])
    #     if notif_obj:
    #         notif_obj.req_nofify = 'shown'


    # @http.route('/hiworth_project_management/notify_update_task_admin', type='json', auth="none")
    # def notify_update_task_admin(self):
    #     user_id = request.session.get('uid')
    #     return request.env['event.event'].sudo().search(
    #         [('reviewer_id','=',user_id),('update_sel', '=', 'bw'), ('update', '!=', 'shown')]
    #     ).get_notifications()

    # @http.route('/hiworth_project_management/notify_ack_update_task', type='json', auth="none")
    # def notify_ack_update_task(self, notif_id, type='json'):
    #     notif_obj = request.env['event.event'].sudo().browse([notif_id])
    #     if notif_obj:
    #         notif_obj.update = 'shown'


# #################################################################################
# #
# #    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# #
# #################################################################################

# import logging
# import werkzeug
# import openerp
# from openerp.addons.auth_signup.res_users import SignupError
# from openerp.addons.web.controllers.main import ensure_db
# from openerp import http
# from openerp.http import request

# _logger = logging.getLogger(__name__)
# class AuthSignupHome(openerp.addons.web.controllers.main.Home):

# 	def do_signup(self, qcontext):
# 		""" Shared helper that creates a res.partner out of a token """
# 		values = dict((key, qcontext.get(key)) for key in ('login', 'name', 'password','street','city','zips','postoffice','country','state_new','phone','mobile','nick_name','dob'))
# 		assert any([k for k in values.values()]), "The form was not properly filled in."
# 		assert values.get('password') == qcontext.get('confirm_password'), "Passwords do not match; please retype them."
# 		self._signup_with_values(qcontext.get('token'), values)
# 		request.cr.commit()

	


