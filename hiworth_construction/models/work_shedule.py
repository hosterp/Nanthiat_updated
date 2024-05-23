from openerp import fields, models, api
from openerp.osv import fields as old_fields, osv, expression
import time
from datetime import datetime
import datetime


class work_schedule(models.Model):
    _name = 'work.schedule'
    
    template_id = fields.Many2one('work.schedule', string="Template")
    is_template = fields.Boolean(string="Is Template")
    name = fields.Char(string='Name')
    project_id = fields.Many2one('project.project',string='Project')
    schedule_line = fields.One2many('work.schedule.line', 'schedule_id', string='schedule Lines')

    @api.one
    def button_template(self):
        self.is_template = True

    @api.onchange('template_id')
    def onchange_template_id(self):
        if self.template_id:
            l1 = []
            d1 = {}
            for val in self.template_id.schedule_line:
                d1 = {
                        'name':val.name,
                        'start_date':val.start_date,
                        'end_date':val.end_date,
                        'status':val.status,
                        'remarks':val.remarks,
                    }
                l1.append(d1)
            self.name = self.template_id.name
            self.project_id = self.template_id.project_id.id or False
            self.schedule_line = l1 
            
    
class work_schedule_line(models.Model):
    _name = 'work.schedule.line' 
    _order = "sequence, id"
    
    name = fields.Many2one('item.of.work',string='Item of Work')
    sequence = fields.Integer('Sequence', help="Gives the sequence order when displaying a list of Projects.")
    start_date = fields.Date('Start Date')
    end_date = fields.Date('Finish Date')
    status = fields.Char('Status')
    remarks = fields.Text('Remarks') 
    schedule_id = fields.Many2one('work.schedule', 'Schedule')
    
    
class project(models.Model):
    _inherit = "project.project"
    
    schedule_ids = fields.One2many('work.schedule', 'project_id', 'Project')