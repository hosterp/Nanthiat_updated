from openerp import fields, models, api


class SiteExpenseReport(models.TransientModel):
    _name = 'site.expense'

    from_date = fields.Date('Date From')
    to_date = fields.Date('Date To')
    project_id = fields.Many2one('project.project', 'Project')

    @api.multi
    def get_labour_payment_products(self):
        # Define the domains for labour attendance and purchase orders based on the given date range
        domain_labour_attendance = [('date', '>=', self.from_date), ('date', '<=', self.to_date)]
        if self.project_id:
            domain_labour_attendance.append(('attendance_id.project_id', '=', self.project_id.id))
        labour_attendance = self.env['labour.attendance'].search(domain_labour_attendance)

        domain_purchase_order = [('date_order', '>=', self.from_date), ('date_order', '<=', self.to_date)]
        if self.project_id:
            domain_purchase_order.append(('project_id', '=', self.project_id.id))
        purchase_orders = self.env['purchase.order'].search(domain_purchase_order)

        # Initialize data structures
        data = {}
        products_map = {}

        # Process labour attendance records
        for rec in labour_attendance:
            print(rec.category_id.name,'category.............................')
            date = rec.date
            if date in data:
                data[date]['total_amount'] += rec.total
            else:
                data[date] = {'total_amount': rec.total, 'total_amount2': 0.0}

        # Process purchase orders and their lines
        for rec in purchase_orders:
            date_str = rec.date_order.split(' ')[0] if rec.date_order else ''
            if date_str in data:
                data[date_str]['total_amount2'] = rec.amount_total
            else:
                data[date_str] = {'total_amount': 0.0, 'total_amount2': rec.amount_total}

            # Collect products related to the purchase order
            for line in rec.order_line:
                if date_str in products_map:
                    products_map[date_str].append(line.product_id)
                else:
                    products_map[date_str] = [line.product_id]
                print(line.product_id.name, 'product....................')

        # Combine data and products for the final output
        datas = []
        for date, info in data.items():
            category_names = [rec.category_id.name for rec in labour_attendance if rec.date == date]
            datas.append({
                'date': date,
                'total_amount': info['total_amount'],
                'total_amount2': info['total_amount2'],
                'category': ', '.join(category_names),
                'products': products_map.get(date, [])
            })

        # Display the combined data for debugging
        for item in datas:
            print("Date: {}, Total Amount: {}, Total Amount2: {}, category:{},Products: {}".format(
                item['date'], item['total_amount'], item['total_amount2'],  item['category'],
                [product.name for product in item['products']]
            ))

        # Return the combined data and a list of all products found
        all_products = [product for products in products_map.values() for product in products]
        return datas, all_products

    def get_category(self, date, products):
        attendance_records = self.env['labour.attendance'].search([('date', '=', date), ('category_id', '!=', False)])
        if attendance_records:
            return attendance_records[0].category_id.name
        return False
    @api.multi
    def prin_site_expense_details_report(self):
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'hiworth_construction.report_site_expense_details_template_view',
            'datas': datas,
            'report_type': 'qweb-pdf',
            #             'context':{'start_date': self.from_date, 'end_date': self.to_date}
        }

    @api.multi
    def view_site_expense_details_report(self):

        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'hiworth_construction.report_site_expense_details_template_view',
            'datas': datas,
            'report_type': 'qweb-html',
            #             'context':{'start_date': self.from_date, 'end_date': self.to_date}
        }
