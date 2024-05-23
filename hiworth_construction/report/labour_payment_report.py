from openerp import fields, models, api


class LabourPaymentReport(models.TransientModel):
    _name='labour.payment.report'

    from_date = fields.Date('Date From')
    to_date = fields.Date('Date To')
    category_id = fields.Many2one('labour.category', 'Category')
    project_id = fields.Many2one('project.project', 'Project')

    @api.multi
    def get_labour_payment_products(self):
        domain = [('date', '>=', self.from_date), ('date', '<=', self.to_date)]
        if self.category_id:
            domain.append(('category_id', '=', self.category_id.id))
        if self.project_id:
            domain.append(('attendance_id.project_id', '=', self.project_id.id))

        purchase_orders = self.env['labour.attendance'].search(domain)

        # products = []
        # for rec in purchase_orders:
        #     print(rec.date,'data........................................')
        return purchase_orders
    @api.multi
    def print_labour_payment_details_report(self):
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'hiworth_construction.report_labour_payment_details_template_view',
            'datas': datas,
            'report_type': 'qweb-pdf',
            #             'context':{'start_date': self.from_date, 'end_date': self.to_date}
        }

    @api.multi
    def view_labour_payment_details_report(self):
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'hiworth_construction.report_labour_payment_details_template_view',
            'datas': datas,
            'report_type': 'qweb-html',
            #             'context':{'start_date': self.from_date, 'end_date': self.to_date}
        }
