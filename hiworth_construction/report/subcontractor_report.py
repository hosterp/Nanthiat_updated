from openerp import fields, models, api


class SubcontractorDailyReport(models.TransientModel):
    _name='subcontractor.wizard'
    
    from_date = fields.Date('Date From')
    to_date = fields.Date('Date To')
    project_id = fields.Many2one('project.project', 'Project')
    contractor = fields.Many2one('sub.contractor.daily.work', 'Contractor')

    @api.multi
    def get_subcontractor_products(self):
        domain = [('date', '>=', self.from_date), ('date', '<=', self.to_date)]

        if self.project_id:
            domain.append(('project_id', '=', self.project_id.id))
        if self.contractor:
            domain.append(('contractor', '=', self.contractor.id))

        purchase_orders = self.env['sub.contractor.daily.work'].search(domain)

        # products = []
        # for rec in purchase_orders:
        #         print(rec.contractor, 'product....................')

        return purchase_orders


    @api.multi
    def print_subcontractor_details_report(self):
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'hiworth_construction.report_subcontrctor_details_template_view',
            'datas': datas,
            'report_type': 'qweb-pdf',
            #             'context':{'start_date': self.from_date, 'end_date': self.to_date}
        }

    @api.multi
    def view_subcontractor_details_report(self):
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'hiworth_construction.report_subcontrctor_details_template_view',
            'datas': datas,
            'report_type': 'qweb-html',
            #             'context':{'start_date': self.from_date, 'end_date': self.to_date}
        }
