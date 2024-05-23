# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Hiworth Project Management',
    'version': '1.1',
    'website': 'https://www.odoo.com/page/project-management',
    'category': 'Project',
    'sequence': 10,
    'summary': 'Projects, Tasks',
    'depends': ['event','hiworth_construction','purchase'
    ],
    'description': """
..
    """,
    'data': [
    'security/project_security.xml',
    'views/project.xml',
    'security/res.country.state.csv',
    'security/ir.model.access.csv',
       'security/ir.rule.csv',
       'views/sequence.xml',
       'views/index.xml',
       'views/messaging_prime.xml',
       'views/task_calendar.xml',
       'views/access_project.xml',
       'views/job_summary.xml',
       'views/customer_file_details.xml',
       'views/work_report.xml',
       'views/account_invoice.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
