# from openerp.exceptions import except_orm, ValidationError
# from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
# from openerp import models, fields, api, _
# from openerp import workflow
# import time
# import datetime
# #from datetime import datetime, timedelta
# from datetime import date
# #from openerp.osv import fields, osv
# from openerp.tools.translate import _
# #from openerp import SUPERUSER_ID
# import openerp.addons.decimal_precision as dp
# #from openerp.osv import fields, osv
# from datetime import timedelta

from openerp.exceptions import except_orm, ValidationError
#from openerp.tools import DEFAULT_SERVER_DateTIME_FORMAT
from openerp import models, fields, api, _
from openerp import workflow
import time
import datetime
#from datetime import datetime, timedelta
from datetime import date
#from openerp.osv import fields, osv
from openerp.tools.translate import _
#from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
#from openerp.osv import fields, osv
from datetime import timedelta




# class account_invoice(models.Model):
#     _inherit = "account.invoice"
#     
#     @api.one
#     @api.depends('invoice_line')
#     def _compute_this_bill_amount_invoice_lines(self): 
#         print "test0===================="    
#         for line in self:
#             print "test1====================" 
#             for lines in line.invoice_line:
#                 print "test2====================" 
#                 line.this_bill_amount_invoice_lines += lines.price_subtotal
#                 print 'test1111111111111111', line.this_bill_amount_invoice_lines                    
#     
#     @api.one
#     @api.depends('invoice_line')
#     def _compute_amount_till_last_bill_invoice_lines(self):     
#         for line in self:
#             for lines in self.invoice_line:
#                 line.amount_till_last_bill_invoice_lines += lines.amount_till_last_bill  
#     
#     @api.one
#     @api.depends('invoice_line')
#     def _compute_amount_upto_date_invoice_lines(self):     
#         for line in self:
#             for lines in self.invoice_line:
#                 line.amount_upto_date_invoice_lines += lines.amount_upto_date
#                 
#                 
#                 
#                 
#                 
#     
#     @api.one
#     @api.depends('addition_lines','invoice_line')
#     def _compute_this_bill_amount_total(self):     
#         for line in self:
#             if self.addition_lines:
#                 this_bill_amount_temp_total=0.0
#                 for lines in self.addition_lines:
#                     this_bill_amount_temp_total += lines.this_bill_amount
#                 line.this_bill_amount_total = this_bill_amount_temp_total +  line.this_bill_amount_invoice_lines                   
#     
#     @api.one
#     @api.depends('addition_lines')
#     def _compute_amount_till_last_bill_total(self):     
#         for line in self:
#             if self.addition_lines:
#                 amount_till_last_bill_temp_total=0.0
#                 for lines in self.addition_lines:
#                     amount_till_last_bill_temp_total += lines.amount_till_last_bill 
#                 line.amount_till_last_bill_total = amount_till_last_bill_temp_total +  line.amount_till_last_bill_invoice_lines
#     
#     @api.one
#     @api.depends('addition_lines','invoice_line')
#     def _compute_amount_upto_date_total(self):     
#         for line in self:
#             if self.addition_lines:
#                 amount_upto_date_temp_total=0.0
#                 for lines in self.addition_lines:
#                     amount_upto_date_temp_total += lines.amount_upto_date
#                 line.amount_upto_date_total = amount_upto_date_temp_total + line.amount_upto_date_invoice_lines
#                 
#     @api.one
#     @api.depends('substraction_lines')
#     def _compute_this_bill_amount_balance(self):     
#         for line in self:
#             if self.substraction_lines:
#                 this_bill_amount_temp_balance=0.0
#                 for lines in self.substraction_lines:
#                     this_bill_amount_temp_balance += lines.this_bill_amount
#                 line.this_bill_amount_balance = line.this_bill_amount_total - this_bill_amount_temp_balance
#     
#     @api.one
#     @api.depends('substraction_lines')
#     def _compute_amount_till_last_bill_balance(self):     
#         for line in self:
#             if self.substraction_lines:
#                 amount_till_last_bill_temp_balance=0.0
#                 for lines in self.substraction_lines:
#                     amount_till_last_bill_temp_balance += lines.amount_till_last_bill
#                 line.amount_till_last_bill_balance = line.amount_till_last_bill_total - amount_till_last_bill_temp_balance
#     
#     @api.one
#     @api.depends('substraction_lines')
#     def _compute_amount_upto_date_balance(self):     
#         for line in self:
#             if self.substraction_lines:
#                 amount_upto_date_temp_balance=0.0
#                 for lines in self.substraction_lines:
#                     amount_upto_date_temp_balance += lines.amount_upto_date
#                 line.amount_upto_date_balance = line.amount_upto_date_total - amount_upto_date_temp_balance    
#                 
#     
#  
#    # invoice_line = fields.One2many('account.invoice.line', 'invoice_id', string='Invoice Lines',
#    #     readonly=True, states={'draft': [('readonly', False)],'open': [('readonly', False)]}, copy=True)
#     addition_lines = fields.One2many('addition.lines', 'addition_line', string='Addition Amounts',
#          states={'draft': [('readonly', False)]}, copy=True)
#     substraction_lines = fields.One2many('substraction.lines', 'substraction_line', string='Substraction Amounts',
#          states={'draft': [('readonly', False)]}, copy=True)
#     this_bill_amount_invoice_lines = fields.Float(compute='_compute_this_bill_amount_invoice_lines', store=True, string='This Bill Amount of Invoice line')
#     amount_till_last_bill_invoice_lines = fields.Float(compute='_compute_amount_till_last_bill_invoice_lines', store=True, string='Amount Till Last Bill of Invoice line')
#     amount_upto_date_invoice_lines = fields.Float(compute='_compute_amount_upto_date_invoice_lines', store=True, string='Amount Upto Date of Invoice line')
#     
#     this_bill_amount_total = fields.Float(compute='_compute_this_bill_amount_total', store=True, string='This Bill Amount')
#  #   qty_till_last_bill_total = fields.Float(string='Qty Till Last Bill', digits= dp.get_precision('Product Price'))
#     amount_till_last_bill_total = fields.Float(compute='_compute_amount_till_last_bill_total', store=True, string='Amount Till Last Bill')
#  #   qty_upto_date_total = fields.Float(string='Qty Upto Date', digits= dp.get_precision('Product Price'))
#     amount_upto_date_total = fields.Float(compute='_compute_amount_upto_date_total', store=True, string='Amount Upto Date')
#     
#     this_bill_amount_balance = fields.Float(compute='_compute_this_bill_amount_balance', store=True, string='This Bill Amount')
#     amount_till_last_bill_balance = fields.Float(compute='_compute_amount_till_last_bill_balance', store=True, string='Amount Till Last Bill')
#     amount_upto_date_balance = fields.Float(compute='_compute_amount_upto_date_balance', store=True, string='Amount Upto Date')
         
class invoice_service_lines(models.Model):
    _name = 'invoice.service.lines'
    
    name = fields.Char(string='Name', index=True)
    discription = fields.Char('Discription')
 #   is_add = fields.Boolean('Is Add')
 #   is_sub = fields.Boolean('Is Subtract')
 #   service_ids1 = fields.Many2one('addition.lines', string='aaaaaaaaaaaaa') 
 #   service_ids2 = fields.Many2one('substraction.lines', string='BBBBBBBBBBBB') 
    
    
class addition_lines(models.Model):
    _name = 'addition.lines'
    
    @api.multi
    @api.depends('this_bill_amount','amount_till_last_bill')
    def _compute_amount_upto_date(self):     
        for line in self:
            line.amount_upto_date=line.this_bill_amount+line.amount_till_last_bill
    
    this_bill_amount = fields.Float(string='This Bill Amount')
    qty_till_last_bill = fields.Float(string='Qty Till Last Bill', digits= dp.get_precision('Product Price'))
    amount_till_last_bill = fields.Float(string='Amount Till Last Bill', digits= dp.get_precision('Product Price'))
    qty_upto_date = fields.Float(string='Qty Upto Date', digits= dp.get_precision('Product Price'))
    amount_upto_date = fields.Float(compute='_compute_amount_upto_date', store=True, string='Amount Upto Date')
    discription = fields.Char(string='Discription')
    service_id1 = fields.Many2one('invoice.service.lines', string='Particulars')
    addition_line = fields.Many2one('account.invoice', string='Invoice')
    
class substraction_lines(models.Model):
    _name = 'substraction.lines'
    
    @api.multi
    @api.depends('this_bill_amount','amount_till_last_bill')
    def _compute_amount_upto_date(self):     
        for line in self:
            line.amount_upto_date=line.this_bill_amount+line.amount_till_last_bill
    
    this_bill_amount = fields.Float(string='This Bill Amount')
    qty_till_last_bill = fields.Float(string='Qty Till Last Bill', digits= dp.get_precision('Product Price'))
    amount_till_last_bill = fields.Float(string='Amount Till Last Bill', digits= dp.get_precision('Product Price'))
    qty_upto_date = fields.Float(string='Qty Upto Date', digits= dp.get_precision('Product Price'))
    amount_upto_date = fields.Float(compute='_compute_amount_upto_date', store=True, string='Amount Upto Date')
    discription = fields.Char(string='Discription')
    service_id2 = fields.Many2one('invoice.service.lines', string='Particulars')
    substraction_line = fields.Many2one('account.invoice', string='Invoice')    


class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'
    
    @api.multi
    @api.depends('quantity','qty_till_last_bill')
    def _compute_qty_upto_date(self):     
        for line in self:
            line.qty_upto_date=line.quantity+line.qty_till_last_bill
            
    @api.multi
    @api.depends('price_subtotal','amount_till_last_bill')
    def _compute_amount_upto_date(self):     
        for line in self:
            line.amount_upto_date=line.price_subtotal+line.amount_till_last_bill
    
    qty_till_last_bill = fields.Float(string='Quantity Till Last Bill', digits= dp.get_precision('Product Price'))
    amount_till_last_bill = fields.Float(string='Quantity Till Last Bill', digits= dp.get_precision('Product Price'))
    qty_upto_date = fields.Float(compute='_compute_qty_upto_date', store=True, string='Quantity Upto Date')
    amount_upto_date = fields.Float(compute='_compute_amount_upto_date', store=True, string='Amount Upto Date')
    
    
    