from openerp import fields, models, api
from openerp.osv import fields as old_fields, osv, expression
import time
from datetime import datetime
import datetime
from openerp.exceptions import except_orm, Warning, RedirectWarning
#from openerp.osv import fields
from openerp import tools
from openerp.tools import float_compare
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from pychart.arrow import default
from cookielib import vals_sorted_by_key
# from pygments.lexer import _default_analyse
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
# from openerp.osv import osv
from openerp import SUPERUSER_ID

from lxml import etree

# 
class Employee_activity_line(models.Model):
    _name = 'employee.activity.line'

    name = fields.Char('Name')
    date = fields.Date('Date')
    project_id = fields.Many2one('project.project', 'Project')
    remarks = fields.Text('Remarks')
    activity_id = fields.Many2one('employee.activity', 'Activity')
    
    _defaults = {
        'date': date.today()
        }

class Employee_Activity(models.Model):
    _name = 'employee.activity'
    _order = 'date desc'
    
    name = fields.Char('Name')
    date = fields.Date('Date')
    employee_id =  fields.Many2one('hr.employee' , 'Engineer')
    activity_line_ids = fields.One2many('employee.activity.line', 'activity_id', 'Lines')
    remark = fields.Text('Remarks')
    
    _defaults = {
        'date': date.today()
        }

                                   
                                   