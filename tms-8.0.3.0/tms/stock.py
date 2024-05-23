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

from openerp.osv import fields, osv
from openerp.tools.translate import _
#from datetime import datetime
#import time
#import decimal_precision as dp
#from months import MONTHS

__author__ = "NEXTMA"
__version__ = "0.1"
__date__ = "02 janvier 2014"

class stock_location(osv.osv):
    u"""emplacement de stock"""
    _inherit = 'stock.location' 
    _name = 'stock.location' 
    
    _columns = {
            'cistern_ok' : fields.boolean(u'Citerne'),
            }
    
    def unlink(self, cr, uid, ids, context=None):
        u"""méthode de suppression"""
        self.write(cr,uid,ids,{'active' : False})
        return True  
    
stock_location()
