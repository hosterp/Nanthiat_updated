# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'TMS Extension',
    'version': '1.0',
    'category': 'Tools',
    'description': """
The module adds the possibility to display data from OpenERP in Google Spreadsheets in real time.
=================================================================================================
""",
    'author': 'Hiworth',
    'website': 'http://www.hiworthsolutions.com',
    'depends': ['fleet','stock','stock_account','web'],
    'data' : [
        'security/tms_security.xml',
        'security/ir.model.access.csv',
        'views/vehicle_odometer_update_view.xml',
        'views/vehicle_details_view.xml',
   #     'hiworth_tms_view.xml',
        'views/hiworth_tms_view2.xml',
        'views/hiworth_tms_menu.xml',
        'views/hiworth_fleet.xml',
        'views/machinery_fuel.xml',
        'views/my_widget.xml',
        'report/route_mapping_report.xml',
        'report/vehicle_report.xml',
        'data/vehicle_category_data.xml',
        'security/hide_sale_pos.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
