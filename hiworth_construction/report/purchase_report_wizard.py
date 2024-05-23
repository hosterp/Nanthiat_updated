from openerp import fields, models, api
import datetime, calendar
from openerp.osv import osv

class PurchaseReport(models.TransientModel):
   
    _name='purchase.report.wizard'

    from_date=fields.Date('Date From')
    to_date=fields.Date('Date To')
    category_id = fields.Many2one('product.category','Category')
    project_id = fields.Many2one('project.project','Project')

    @api.multi
    def get_purchase_products(self):


        purchase_order = self.env['purchase.order'].search([('date_order','>=',self.from_date),('date_order','<=',self.to_date),('project_id','=',self.project_id.id)])
        res_list = []
        if self.category_id:
            for purchase in purchase_order:
                for purchase_order_line in purchase.order_line:
                    if purchase_order_line.product_id.categ_id.id == self.category_id.id:
                        res = {}
                        res.update({'product_id':purchase_order_line.product_id.name,
                                    'supplier_id':purchase.partner_id.name,
                                    'total':purchase_order_line.total})
                        res_list.append(res)
                        
        return res_list
        


    @api.multi
    def print_purchase_report(self):


        
        
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context':self._context,
        }
        return{
            'type' : 'ir.actions.report.xml',
            'report_name' : 'hiworth_construction.report_purchase_template_view',
            'datas': datas,
            'report_type': 'qweb-pdf',
#             'context':{'start_date': self.from_date, 'end_date': self.to_date}
        }

    @api.multi
    def view_purchase_report(self):


        
        
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context':self._context,
        }
        return{
            'type' : 'ir.actions.report.xml',
            'report_name' : 'hiworth_construction.report_purchase_template_view',
            'datas': datas,
            'report_type': 'qweb-html',
#             'context':{'start_date': self.from_date, 'end_date': self.to_date}
        }
