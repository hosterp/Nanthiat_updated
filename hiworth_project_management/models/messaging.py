from openerp import models, fields, api, _
import uuid
import sys, zipfile, xml.dom.minidom
import pytz

class GeneralMessages(models.Model):
    _name = 'general.message'
    _order = 'id desc'

    from_id = fields.Many2one('res.users','From')
    to_id = fields.Many2one('res.users','To')
    message = fields.Text('Message')
    date_today = fields.Datetime('Date')
    status = fields.Selection([('shown', 'shown'), ('draft', 'draft')], default='draft')

    @api.multi
    def get_notifications(self):
        result = []
        for obj in self:
            result.append({
                'title': obj.message,
                'user':obj.from_id.name,
                'logged':obj.to_id.name,
                'status': obj.status,
                'id': obj.id,
            })
        return result



    @api.multi
    def reply_message(self):
        ids = [self.from_id.id]
        view_ref = self.env['ir.model.data'].get_object_reference('hiworth_project_management', 'view_project_general_message_reply')
        view_id = view_ref[1] if view_ref else False
        res = {
           'type': 'ir.actions.act_window',
           'name': _('Reply'),
           'res_model': 'im_chat.message.new',
           'view_type': 'form',
           'view_mode': 'form',
           'view_id': view_id,
           'target': 'current',
           'context': {'default_reply':self.message,'default_user_ids':[(6, 0, ids)]}
       }

        return res

class IChat(models.Model):
    _inherit = 'im_chat.message'

    to_id = fields.Many2one('im_chat.session','Session To', select=True, ondelete='cascade')
    to_is = fields.Many2one('res.users','To')

    _defaults = {
        'from_id':lambda obj, cr, uid, ctx=None: uid,
        }



class ImChatMessage(models.Model):
    _name = 'im_chat.message.new'
    _order = 'id desc'





    from_id = fields.Many2one('res.users','From')
    to_id = fields.Many2one('res.users','To')
    user_ids =  fields.Many2many('res.users', string='To',required=True)
    message = fields.Text('Leave a Message Here..')
    user_id = fields.Many2one('res.users', 'User')
    date_today = fields.Datetime('Date',default=fields.Datetime.now())
    state = fields.Selection([
            ('draft','Draft'),
            ('read','Read'),
            ('confirm','Confirmed'),
        ], string='Status', index=True, readonly=True, default='draft',
         copy=False)
    status = fields.Selection([
            ('unread','Unread'),
            ('read','Read'),
        ], string='Status', default='unread',change_default=True)
    bool_bool = fields.Boolean(default=False)
    to_values = fields.Char(compute="_get_to_ids")
    reply = fields.Text('Reply')



    _defaults = {
        'from_id':lambda obj, cr, uid, ctx=None: uid,
        'user_id': lambda obj, cr, uid, ctx=None: uid,
        }

    @api.multi
    def send_message(self):
        if self.user_ids:
            for values in self.user_ids:
                # print"julyyyyyyyyyyyyyyyyyyyyyyyyyyyy",values.id,values.name
                self.env['general.message'].create({'date_today':fields.Datetime.now(),'from_id':self.from_id.id,'to_id':values.id,'message':self.message})



    @api.one
    @api.depends('user_ids')
    def _get_to_ids(self):
        self.to_values = ''
        for line in self:
            if self.user_ids:
                for val in self.user_ids:
                    line.to_values = line.to_values+val.name +','





    @api.multi
    def mark_as_read(self):
        self.status = 'read'
        self.state = 'read'

    @api.multi
    def delete_message(self):
        self.state = 'confirm'
        period_obj = self.env['im_chat.message.delete']
        period_obj.create( {
                    'from_id':self.from_id.id,
                    'to_id':self.to_id.id,
                    'message':self.message,
                    'state':self.state
                })
        models.Model.unlink(self)


class ImChatMessage(models.Model):
    _name = 'im_chat.message.req'
    _order = 'id desc'

    from_id = fields.Many2one('res.users','From',readonly=True)
    nick_name = fields.Char('Nick Name',related='from_id.partner_id.nick_name',readonly=True)
    req_gen = fields.Boolean('REQGEN',default=False)
    no_edit = fields.Boolean(default=False)
    to_id = fields.Many2one('res.users','To')
    cc_ids = fields.Many2many('res.users','message_cc_rel','message_id','user_id',string='Cc')
    cc_id = fields.Many2one('res.users','Ccs')
    message = fields.Text('Leave a Message Here..',required=True)
    user_id = fields.Many2one('res.users', 'User')
    state = fields.Selection([('new','New'),
            ('draft','Draft'),
            ('pending','Pending'),
            ('approved','Approved'),
        ], string='Status', readonly=True, default='approved',
         copy=False)
    bool_msg = fields.Boolean(default=False)
    require = fields.Boolean(default=True)
    reply = fields.Text('Reply')
    date_today = fields.Datetime('Date',default=fields.Datetime.now)
    convert_task = fields.Boolean(default=False)
    related_project = fields.Many2one('project.project','Related Project')
    admin = fields.Many2one('res.users', 'Admin')
    message_type = fields.Selection([('general','General'),('official','Official')],string="Messaging Type",required=True,default="general")
    status = fields.Selection([('shown', 'shown'), ('draft', 'draft')], default='draft')
    status1 = fields.Selection([('shown', 'shown'), ('draft', 'draft')], default='draft')
    add_member = fields.One2many('assigned.member','as_id')
    attachment_idss = fields.One2many('ir.attachment','att_ids')
    has_attachment = fields.Boolean('Has Attachment',default=False)
    sent = fields.Boolean(default=False)
    delete_msg = fields.Boolean(default=False)
    done_mem = fields.Boolean(default=False)
    cc_bool = fields.Boolean(default=False)
    req_nofify = fields.Selection([('draft','Draft'),('shown','Shown')],default='draft')

    @api.multi
    def delete_msg_inbox(self):
        self.delete_msg = True
        return {
                'name': 'Inbox',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'im_chat.message.req',
                'domain': [('to_id','=',self.to_id.id),('require','=',True),('delete_msg','=',False),('state','=','approved')],

                'target': 'current',
                'type': 'ir.actions.act_window',
                'context': {},

            }

    @api.multi
    def back_to_inbox(self):
        self.delete_msg = False
        return {
                'name': 'Deleted Messages',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'im_chat.message.req',
                'domain': [('to_id','=',self.to_id.id),('delete_msg','=',True)],

                'target': 'current',
                'type': 'ir.actions.act_window',
                'context': {},

            }



    _defaults = {
        'from_id':lambda obj, cr, uid, ctx=None: uid,
        'user_id': lambda obj, cr, uid, ctx=None: uid,
        'admin': lambda obj, cr, uid, ctx=None: 1,
        }

    @api.onchange('attachment_idss')
    def onchange_attachment_ids(self):
        if self.attachment_idss:
            self.has_attachment = True
        else:
            self.has_attachment = False

    @api.onchange('message_type')
    def onchange_req_gen(self):
        if self.message_type == 'general' or self.message_type == 'official':
            self.req_gen = True
        else:
            self.req_gen = False


    @api.multi
    def general_message(self):
        self.state = 'new'

    @api.model
    def create(self, vals):
        result = super(ImChatMessage, self).create(vals)
        if result.cc_ids:
            rec_attc = []
            if result.attachment_idss:
                for att in result.attachment_idss:
                    rec_attc.append((0,0,{'name':att.name,'datas':att.datas}))
            print "rec_attc=============", rec_attc
            for ccs in result.cc_ids:
                values_cc = {
                    'from_id' :result.from_id.id,
                    'require': True,
                    'to_id' :result.to_id.id,
                    'message_type':result.message_type,
                    'req_gen' :False if result.message_type == 'requirement' else True,
                    'cc_ids': [(6, 0, [i.id for i in result.cc_ids])],
                    'cc_id':ccs.id,
                    'related_project':result.related_project.id,
                    'date_today':fields.Datetime.now(),
                    'message':result.message,
                    'attachment_idss':rec_attc,
                    'no_edit':True,
                    'cc_bool':True,
                    }
                create_cc = super(ImChatMessage, self).create(values_cc)
            # values_cc_to = {
            #         'from_id' :result.from_id.id,
            #         'to_id' :result.to_id.id,
            #         'require': True if result.to_id.customer == True else False,
            #         'message_type':result.message_type,
            #         'cc_ids': [(6, 0, [i.id for i in result.cc_ids])],
            #         'cc_id':result.to_id.id,
            #         'req_gen' :False if result.message_type == 'requirement' else True,
            #         'related_project':result.related_project.id,
            #         'date_today':fields.Datetime.now(),
            #         'attachment_idss':rec_attc,
            #         'message':result.message,
            #         'no_edit':True,
            #         'cc_bool':True,
            #         }
            # create_cc_to = super(ImChatMessage, self).create(values_cc_to)
        # else:
        result.cc_id = result.to_id.id

        if result.no_edit == False:
            result.no_edit = True
        res_id = [result]
        if result.from_id.customer == True and result.message_type == 'requirement':
            if result.to_id.sudo().employee_id.employee_type == 'employee':
                rec = self.env['project.project'].search([('id','=',result.related_project.id)])
                if rec:
                    values1 = {
                    'from_id' :result.from_id.id,
                    'to_id' :rec.user_id.id,
                    'message_type':result.message_type,
                    'related_project':result.related_project.id,
                    'date_today':fields.Datetime.now(),
                    'message':result.message,
                    'no_edit':True,
                    'sent':True
                    }
                    values2 = {
                    'from_id' :result.from_id.id,
                    'to_id' :1,
                    'message_type':result.message_type,
                    'related_project':result.related_project.id,
                    'date_today':fields.Datetime.now(),
                    'message':result.message,
                    'no_edit':True,
                    'sent':True
                    }
                    create1 = super(ImChatMessage, self).create(values1)
                    create2 = super(ImChatMessage, self).create(values2)
        return result

    @api.multi
    def task_message(self):
        self.req_gen = True
        self.done_mem = False
        if self.env.user.id != 1:
            print "aaaaaaaaaaaaaaaa"
            rec = self.env['im_chat.message.req'].search([('message_type','=','requirement'),('from_id','=',self.from_id.id),('to_id','=',1),('message','=',self.message),('related_project','=',self.related_project.id)])
            print "bbbbbbbbbbbbbbbbbbbb", rec
            if rec:
                record = []
                for val in self.add_member:
                    record.append({'assigned_to':val.assigned_to.id})
                print "ccccccccccccccccccccc" , record
                rec.add_member = record


    @api.multi
    def get_notifications(self):
        result = []
        for obj in self:
            result.append({
                'title': obj.message,
                'title1': obj.reply,
                'user':obj.from_id.name,
                'status': obj.status,
                'status1': obj.status1,
                'message_type':(obj.message_type).title(),
                'id': obj.id,
                'id1':obj.from_id.id,
                'req_nofify': obj.req_nofify
            })
        return result


    @api.onchange("related_project")
    def onchange_related_project_line(self):
        if self.from_id:
            ids = []
            if self.from_id.partner_id.customer == True:
                record = self.env['project.project'].search([('partner_id','=',self.from_id.partner_id.id)])

                if record:
                    for item in record:
                        ids.append(item.id)
                    return {'domain': {'related_project': [('id', 'in', ids)]}}
                else:
                    return {'domain': {'related_project': [('id', 'in', ids)]}}
            else:
                return {'domain': {'related_project': [('id', 'in', ids)]}}

    @api.onchange("to_id","related_project","message_type","from_id")
    def onchange_to_id_line(self):
        ids = []
        if self.from_id.partner_id.customer == True and not self.env.user.id == 1:
            if self.related_project:
                record = self.env['project.project'].search([('partner_id','=',self.from_id.partner_id.id),('id','=',self.related_project.id)])
                if record:
                    if record.members:
                        for item in record.members:
                            ids.append(item.id)
                        return {'domain': {'to_id': [('id', 'in', ids)]}}
                    else:
                        return {'domain': {'to_id': [('id', 'in', ids)]}}
                else:
                    return {'domain': {'to_id': [('id', 'in', ids)]}}
            else:
                records = self.env['project.project'].search([('partner_id','=',self.from_id.partner_id.id)])
                for record in records:
                    if record.members:
                        for item in record.members:
                            ids.append(item.id)
                return {'domain': {'to_id': [('id', 'in', ids)]}}
        else:
            rec = self.env['res.users'].search([])
            for user in rec:
                ids.append(user.id)
            return {'domain': {'to_id': [('id', 'in', ids)]}}



    @api.onchange('to_id')
    def _onchange_to_id_cc(self):
        if self.to_id:
            list = []
            rec = self.env['res.users'].search([('id','!=',self.to_id.id)])
            for record in rec:
                list.append(record.id)
            return {'domain': {'cc_ids': [('id', 'in', list)]}}



    @api.multi
    def task_convert(self):
        view_ref = self.env['ir.model.data'].get_object_reference('hiworth_project_management', 'view_project_employee_charge_form')
        view_id = view_ref[1] if view_ref else False
        res = {
           'type': 'ir.actions.act_window',
           'name': _('Employee InCharge'),
           'res_model': 'employee.charge',
           'view_type': 'form',
           'view_mode': 'form',
           'view_id': view_id,
           'target': 'new',
           'context': {'default_rec':self.id}
       }

        return res

    @api.multi
    def approved_message(self):
        self.state = 'approved'
        self.require = True
        self.bool_msg = True
        self.done_mem = False
        self.status = 'draft'
        rec = self.env['project.project'].search([('partner_id','=',self.to_id.partner_id.id),('id','=',self.related_project.id)])

    @api.multi
    def reply_message(self):

        ids = self.from_id.id
        view_ref = self.env['ir.model.data'].get_object_reference('hiworth_project_management', 'view_project_message_requirement_form')
        view_id = view_ref[1] if view_ref else False
        res = {
           'type': 'ir.actions.act_window',
           'name': _('Reply'),
           'res_model': 'im_chat.message.req',
           'view_type': 'form',
           'view_mode': 'form',
           'view_id': view_id,
           'target': 'current',
           'context': {'default_cc_ids':[(6, 0, [i.id for i in self.cc_ids])],'default_done_mem':False,'default_status':'draft' if self.message_type != 'requirement' else 'shown','default_message_type':self.message_type,'default_related_project':self.related_project.id,'default_require':True if self.message_type != 'requirement' else False,'default_reply':self.message,'default_to_id':ids,'default_state':'pending' if self.message_type == 'requirement' else 'approved','default_bool_msg':True,'default_req_gen':True}
       }

        return res


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.onchange('datas','datas_fname')
    def onchange_datas(self):
        if self.datas or self.datas_fname:
            self.name = self.datas_fname

    @api.multi
    def set_image_gallery(self):
        if self.datas:
            record = []
            att_id = self.env['ir.attachment'].create({'datas':self.datas,'name':self.name})
            record.append(att_id.id)
            for att in self.gallery_img.site_images:
                record.append(att.id)
            print "record==================", record
            self.gallery_img.write({'site_images' : [(6, 0, record)]})


    @api.multi
    def set_image(self):
        if self.datas:
            record = []
            att_id = self.env['ir.attachment'].create({'datas':self.datas,'name':self.name})
            record.append(att_id.id)
            for att in self.project_image.site_image:
                record.append(att.id)
            print "record==================", record
            self.project_image.write({'site_image' : [(6, 0, record)]})

    @api.multi
    def view_image(self):
        view_ref = self.env['ir.model.data'].get_object_reference('hiworth_project_management', 'view_ir_attachment_form_view_image')
        view_id = view_ref[1] if view_ref else False
        res = {
           'type': 'ir.actions.act_window',
           'name': _('View Image'),
           'res_model': 'ir.attachment',
           'view_type': 'form',
           'view_mode': 'form',
           'view_id': view_id,
           'target': 'new',
           'context': {'default_name':self.name,'default_datas':self.datas}
       }
     
        return res
        



    att_ids = fields.Many2one('im_chat.message.req', )
    project_image = fields.Many2one('project.project')
    # gallery_img = fields.Many2one('gallery.project', required=False)
    gallery = fields.Boolean(default=False)
    drawing_id = fields.Many2one('project.project')

    # pic_id = fields.Many2one('project.project')


# class ProjectAttachment(models.Model):
#     _inherit = 'project.attachment'
#
#     att_ids = fields.Many2one('im_chat.message.req')

class TaskMessage(models.Model):
    _name = 'task.message'
    _order = 'id desc'

    rec = fields.Many2one('im_chat.message.req')
    from_id = fields.Many2one('res.users',string='From')
    to = fields.Many2one('res.users',string="To")
    message = fields.Char('Message')
    reply = fields.Char('Reply')
    manager = fields.Many2one('res.users','Manager')
    convert_task = fields.Boolean(default=False)
    project = fields.Many2one('project.project','Project',readonly=True)
    date = fields.Datetime('Date')
    assigned = fields.Many2one('res.users','Assigned To')
    admin = fields.Many2one('res.users', 'Admin')
    status = fields.Selection([('shown', 'shown'), ('draft', 'draft')], default='draft')

    _defaults = {
        'admin': lambda obj, cr, uid, ctx=None: 1,
        }

    @api.multi
    def get_notifications(self):
        result = []
        for obj in self:
            result.append({
                'title': obj.message,
                'user':obj.from_id.name,
                'logged':obj.to.name,
                'status': obj.status,
                'id': obj.id,
            })
        return result



    @api.multi
    def task_convert(self):
        view_ref = self.env['ir.model.data'].get_object_reference('hiworth_project_management', 'view_project_employee_charge_form')
        view_id = view_ref[1] if view_ref else False
        res = {
           'type': 'ir.actions.act_window',
           'name': _('Employee InCharge'),
           'res_model': 'employee.charge',
           'view_type': 'form',
           'view_mode': 'form',
           'view_id': view_id,
           'target': 'new',
           'context': {'default_recs':self.id,'default_employee':self.assigned.id}
       }

        return res

class TaskMessage(models.Model):
    _name = 'task.mes'

    rec = fields.Many2one('im_chat.message.req')
    from_id = fields.Many2one('res.users',string='From')
    to = fields.Many2one('res.users',string="To")
    message = fields.Char('Message')
    manager = fields.Many2one('res.users','Manager')
    convert_task = fields.Boolean(default=False)
    project = fields.Many2one('project.project','Project',readonly=True)
    date = fields.Datetime('Date')
    assigne = fields.Many2one('res.users','Assigned To')
    start_time = fields.Datetime('Starting Time')




    @api.model
    def create(self, vals):
        result = super(TaskMessage, self).create(vals)
        return result

    @api.multi
    def confirm_task(self):
        self.env['task.message'].create({
                                'from_id':self.to.id,
                                'to':self.from_id.id,
                                'message':self.message,
                                'date':self.date,
                                'assigned':self.assigned.id,
                                'project':self.project.id
            })
        self.rec.state = 'new'
        return



class AssigningMember(models.Model):
    _name = 'assigned.member'

    assigned_ids = fields.Many2one('task.mes')
    as_id = fields.Many2one('im_chat.message.req')
    assigned_to = fields.Many2one('res.users','Job Assigned To')

    @api.multi
    def add_member(self):
        self = self.sudo()
        return {
            'name': 'Task conversation_state',
            'view_type': 'form',
            'view_mode': 'calendar,tree,form',
            'res_model': 'event.event',
            'domain': [('user_id', '=', self.assigned_to.id)],
            'target': 'current',
            'type': 'ir.actions.act_window',
            'context': {'default_user_id':self.assigned_to.id,'default_name':self.as_id.message,'default_project_id':self.as_id.related_project.id,'default_civil_contractor':self.as_id.related_project.partner_id.id,'default_project_manager':self.as_id.related_project.user_id.id}
        }

class EmployeeCharge(models.Model):
    _name = 'employee.charge'

    task_category = fields.Many2one('event.type','Task Category')
    employee = fields.Many2one('res.users','Assigned To')
    recs = fields.Many2one('task.message')

    @api.multi
    def confirm_employee(self):
        self.recs.convert_task = True
        uom = self.env['product.uom'].search([])
        rec = self.env['project.project'].search([('partner_id','=',self.recs.to.partner_id.id),('id','=',self.recs.project.id)])
        if rec:
            self.env['event.event'].sudo().create({'event_project':rec.id,'type':self.task_category.id,'date_begin':fields.Datetime.now(),'date_end':fields.Datetime.now(),'project_manager':rec.user_id.id,'name':self.recs.message,'project_id':rec.id,'civil_contractor':self.recs.to.id,'user_id':self.employee.id})



class ImChatMessageDelete(models.Model):
    _name = 'im_chat.message.delete'


    from_id = fields.Many2one('res.users','From')
    to_id = fields.Many2one('res.users','To')
    message = fields.Text('Leave a Message Here..')
    user_id = fields.Many2one('res.users', 'User')
    state = fields.Selection([
            ('draft','Draft'),
            ('read','Read'),
            ('confirm','Confirmed'),
        ], string='Status', index=True, readonly=True, default='draft',
         copy=False)

    _defaults = {
        'from_id':lambda obj, cr, uid, ctx=None: uid,
        'user_id': lambda obj, cr, uid, ctx=None: uid,
        }

    @api.multi
    def back_to_inbox(self):
        self.state = 'confirm'
        period_obj = self.env['im_chat.message.new']
        period_obj.create( {
                    'from_id':self.from_id.id,
                    'to_id':self.to_id.id,
                    'message':self.message,
                })
        models.Model.unlink(self)
