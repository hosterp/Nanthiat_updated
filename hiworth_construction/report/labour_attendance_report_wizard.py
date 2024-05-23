from openerp import fields, models, api
import datetime, calendar
from openerp.osv import osv

class LabourAttendanceReport(models.TransientModel):
   
    _name='labour.attendance.report'

    from_date=fields.Date('Date From')
    to_date=fields.Date('Date To')
    location_id = fields.Many2one('stock.location','Location')
    category_id = fields.Many2one('labour.category','Category')


    @api.multi
    def get_labour_attendance(self):

        res = {}
        res_list = []
        labour_category = self.env['partner.daily.statement'].search([('date','>=',self.from_date),('date','<=',self.to_date),('location_ids','=',self.location_id.id)])
        if self.category_id:
            for labour in labour_category:
                for lab_line in labour.attendance_ids:
                    if lab_line.category_id.id == self.category_id.id:
                        res_list.append(labour)
            return res_list
        else:
            return labour_category

           
        
    @api.multi
    def get_labour_category(self):

        res = {}
        res_list = []
        labour_category = self.env['partner.daily.statement'].search([('date','>=',self.from_date),('date','<=',self.to_date),('location_ids','=',self.location_id.id)])
        if self.category_id:
            for labour in labour_category:
                for lab_line in labour.attendance_ids:
                    if lab_line.category_id.id == self.category_id.id:
                        res_list.append(lab_line)
            return res_list
        else:
            return labour_category


    @api.multi
    def print_labour_attendance_report(self):


        
        
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context':self._context,
        }
        return{
            'type' : 'ir.actions.report.xml',
            'report_name' : 'hiworth_construction.report_labour_attendance_trmplate_view',
            'datas': datas,
            'report_type': 'qweb-pdf',
#             'context':{'start_date': self.from_date, 'end_date': self.to_date}
        }

    @api.multi
    def view_labour_attendance_report(self):


        
        
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context':self._context,
        }
        return{
            'type' : 'ir.actions.report.xml',
            'report_name' : 'hiworth_construction.report_labour_attendance_trmplate_view',
            'datas': datas,
            'report_type': 'qweb-html',
#             'context':{'start_date': self.from_date, 'end_date': self.to_date}
        }
