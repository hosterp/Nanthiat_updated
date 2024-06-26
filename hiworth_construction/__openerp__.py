
{
    'name': 'Hiworth Construction Management',
    'version': '1.0',
    'category': 'Project',
    'sequence': 21,
    'description': """ Project Cost Estimation """,
    'depends': ['sale','project','mrp','purchase','document','hr','hiworth_accounting','hiworth_hr_attendance','auditlog','hiworth_tms'],
    'data': [
         'security/user_groups.xml',
         'security/ir.model.access.csv',
         'security/ir.rule.csv',
         'security/hide_sale_manufacturing.xml',
         # 'security/security.xml',
         'views/work_order_sequence.xml',
         'views/contractor_bill_sequence.xml',
         'report/purchase_report.xml',
         'report/alter_default_header_footer.xml',
         'report/project.xml',
         'report/task.xml',
         'report/material_request.xml',
         'report/location_wise_report.xml',
         'report/stock_report.xml',
         'report/common_report_alteration.xml',
         'report/project_report.xml',
         'views/invoice_action_data.xml',
         'views/construction_project_details_view.xml',
         'views/counstruction_menu_view.xml',
         'views/purchase_order_action_data.xml',
         'views/default_project_stages.xml',
         'views/activity_view.xml',
         'views/hiworth_invoice.xml',
         'views/hiworth_accounting_view.xml',
         'views/work_order.xml',
         'views/admin_saction_records.xml',
         'report/product_to_location_report.xml',
         'report/stock_move_report.xml',
         'wizard/stock_transfer_details.xml',
         'views/daily_progress_report.xml',
         'views/work_shedule.xml',
         'views/employee_activity.xml',
         'views/delay_report.xml',
         'views/progress_report.xml',

         'report/activity_reports.xml',
         'data/defaultdata.xml',
         'views/account_payment_schedule.xml',
         'report/contractor_invoices_report.xml',
         'report/task_report_wizarad.xml',
         'views/material_request.xml',
         'views/project_stages.xml',
         'views/driver_daily_stmt.xml',
         'views/daily_statment_sequence.xml',
         'views/partner_daily_statement.xml',
         'report/driver_daily_report.xml',
         'report/partner_daily_report.xml',
         'views/rent_vehicles_statement.xml',
         'report/report.xml',
         'views/site_purchase.xml',
         'views/sequence.xml',
         'views/product_price_data.xml',
         'views/tendor_views.xml',
         'views/action_menu_hide.xml',
         'views/planning.xml',
         'views/finance_views.xml',
         'views/nextday_settlement.xml',
         'views/supervisor_payment_views.xml',
         'report/tender_security_report.xml',
         'report/hiworth_vehicle_status_view.xml',
         'report/labour_attendance_report.xml',
         # 'report/rent_vehicle_report.xml'
         'views/popup_notification.xml',
         'report/view_purchase_details.xml',
         'report/View_payment_details.xml',
         'report/subcontractor_daily_report.xml',
         'report/labour_payment_report.xml',
         'report/site_expense_report.xml',



    ],

    'qweb': [
                'static/src/xml/popup_notifications.xml',
            ],

    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
