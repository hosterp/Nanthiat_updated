from openerp import fields, models, api, _
from openerp.osv import osv, expression
from openerp.exceptions import Warning as UserError
import re


class Number2Words(object):


        def __init__(self):
            '''Initialise the class with useful data'''

            self.wordsDict = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven',
                              8: 'eight', 9: 'nine', 10: 'ten', 11: 'eleven', 12: 'twelve', 13: 'thirteen',
                              14: 'fourteen', 15: 'fifteen', 16: 'sixteen', 17: 'seventeen',
                              18: 'eighteen', 19: 'nineteen', 20: 'twenty', 30: 'thirty', 40: 'forty',
                              50: 'fifty', 60: 'sixty', 70: 'seventy', 80: 'eighty', 90: 'ninty' }

            self.powerNameList = ['thousand', 'lac', 'crore']


        def convertNumberToWords(self, number):

            # Check if there is decimal in the number. If Yes process them as paisa part.
            formString = str(number)
            if formString.find('.') != -1:
                withoutDecimal, decimalPart = formString.split('.')

                paisaPart =  str(round(float(formString), 2)).split('.')[1]
                inPaisa = self._formulateDoubleDigitWords(paisaPart)

                formString, formNumber = str(withoutDecimal), int(withoutDecimal)
            else:
                # Process the number part without decimal separately
                formNumber = int(number)
                inPaisa = None

            if not formNumber:
                return 'zero'

            self._validateNumber(formString, formNumber)

            inRupees = self._convertNumberToWords(formString)

            if inPaisa:
                return '%s and %s paisa' % (inRupees.title(), inPaisa.title())
            else:
                return '%s' % inRupees.title()


        def _validateNumber(self, formString, formNumber):

            assert formString.isdigit()

            # Developed to provide words upto 999999999
            if formNumber > 999999999 or formNumber < 0:
                raise AssertionError('Out Of range')


        def _convertNumberToWords(self, formString):

            MSBs, hundredthPlace, teens = self._getGroupOfNumbers(formString)

            wordsList = self._convertGroupsToWords(MSBs, hundredthPlace, teens)

            return ' '.join(wordsList)


        def _getGroupOfNumbers(self, formString):

            hundredthPlace, teens = formString[-3:-2], formString[-2:]

            msbUnformattedList = list(formString[:-3])

            #---------------------------------------------------------------------#

            MSBs = []
            tempstr = ''
            for num in msbUnformattedList[::-1]:
                tempstr = '%s%s' % (num, tempstr)
                if len(tempstr) == 2:
                    MSBs.insert(0, tempstr)
                    tempstr = ''
            if tempstr:
                MSBs.insert(0, tempstr)

            #---------------------------------------------------------------------#

            return MSBs, hundredthPlace, teens


        def _convertGroupsToWords(self, MSBs, hundredthPlace, teens):

            wordList = []

            #---------------------------------------------------------------------#
            if teens:
                teens = int(teens)
                tensUnitsInWords = self._formulateDoubleDigitWords(teens)
                if tensUnitsInWords:
                    wordList.insert(0, tensUnitsInWords)

            #---------------------------------------------------------------------#
            if hundredthPlace:
                hundredthPlace = int(hundredthPlace)
                if not hundredthPlace:
                    # Might be zero. Ignore.
                    pass
                else:
                    hundredsInWords = '%s hundred' % self.wordsDict[hundredthPlace]
                    wordList.insert(0, hundredsInWords)

            #---------------------------------------------------------------------#
            if MSBs:
                MSBs.reverse()

                for idx, item in enumerate(MSBs):
                    inWords = self._formulateDoubleDigitWords(int(item))
                    if inWords:
                        inWordsWithDenomination = '%s %s' % (inWords, self.powerNameList[idx])
                        wordList.insert(0, inWordsWithDenomination)

            #---------------------------------------------------------------------#
            return wordList


        def _formulateDoubleDigitWords(self, doubleDigit):

            if not int(doubleDigit):
                # Might be zero. Ignore.
                return None
            elif self.wordsDict.has_key(int(doubleDigit)):
                # Global dict has the key for this number
                tensInWords = self.wordsDict[int(doubleDigit)]
                return tensInWords
            else:
                doubleDigitStr = str(doubleDigit)
                tens, units = int(doubleDigitStr[0])*10, int(doubleDigitStr[1])
                tensUnitsInWords = '%s %s' % (self.wordsDict[tens], self.wordsDict[units])
                return tensUnitsInWords

class MasterBlock(models.Model):
    _name = 'master.block'

    name = fields.Char(string="Block")

    @api.constrains('name')
    def _check_duplicate_name(self):
        names = self.search([])
        for c in names:
            if self.id != c.id:
                if self.name.lower() == c.name.lower() or self.name.lower().replace(" ", "") == c.name.lower().replace(" ", ""):
                    raise osv.except_osv(_('Error!'), _('Error: name must be unique'))
                else:
                    pass

class MasterPanchayath(models.Model):
    _name = 'master.panchayath'

    name = fields.Char(string="Panchayath")

    @api.constrains('name')
    def _check_duplicate_name(self):
        names = self.search([])
        for c in names:
            if self.id != c.id:
                if self.name.lower() == c.name.lower() or self.name.lower().replace(" ", "") == c.name.lower().replace(" ", ""):
                    raise osv.except_osv(_('Error!'), _('Error: name must be unique'))
                else:
                    pass

class MasterDistrict(models.Model):
    _name = 'master.district'

    name = fields.Char(string="District")

    @api.constrains('name')
    def _check_duplicate_name(self):
        names = self.search([])
        for c in names:
            if self.id != c.id:
                if self.name.lower() == c.name.lower() or self.name.lower().replace(" ", "") == c.name.lower().replace(" ", ""):
                    raise osv.except_osv(_('Error!'), _('Error: name must be unique'))
                else:
                    pass

class BillOfQuantity(models.Model):
    _name = 'bill.of.quantity'
    _rec_name = "name_of_work"

    tender_inviting_authority = fields.Char(string="Tender Inviting Authority")
    name_of_work = fields.Many2one('project.project',string="Name of Work")
    contract_no = fields.Char(string="Contract No")
    bidder_name = fields.Many2one('res.partner',domain="[('contractor', '=', True)]", string="Bidder Name")
    line_ids = fields.One2many('bill.of.quantity.line','line_id',string="BOQ Info")
    extra_line_ids = fields.One2many('bill.of.quantity.line','extra_line_id',string="Extra Items")  
    package_no = fields.Char(string="Package No.")
    agent_no = fields.Char(string="Agent No.")
    date = fields.Date(string="Date", default=fields.Date.today())
    block_id = fields.Many2one('master.block',string="Block")
    panchayath_id = fields.Many2one('master.panchayath',string="Panchayath")
    district_id = fields.Many2one('master.district',string="District")
    block = fields.Char(string="Block")
    district = fields.Char(string="District")
    panchayath = fields.Char(string="Panchayath")
    # invoice_id = fields.Many2one('account.invoice')

    @api.model
    def create(self, vals):     
        block_id = False
        panchayath_id = False
        district_id = False
        
        #Block
        if vals.get('block'):
            block_id = self.env['master.block'].search([('name','=',vals.get('block'))]).id
            if not block_id:
                block_id = self.env['master.block'].create({'name':vals.get('block')}).id
        vals['block_id'] = block_id

        #Panchayath
        if vals.get('panchayath'):
            panchayath_id = self.env['master.panchayath'].search([('name','=',vals.get('panchayath'))]).id
            if not panchayath_id:
                panchayath_id = self.env['master.panchayath'].create({'name':vals.get('panchayath')}).id
        vals['panchayath_id'] = panchayath_id

        #District
        if vals.get('district'):
            district_id = self.env['master.district'].search([('name','=',vals.get('district'))]).id
            if not district_id:
                district_id = self.env['master.district'].create({'name':vals.get('district')}).id
        vals['district_id'] = district_id

        result = super(BillOfQuantity, self).create(vals)           
        return result



    @api.multi
    def view_bill(self):

        view_id = self.env.ref('hiworth_boq.first_bill_invoice_form_123').id
        return{
            'name': 'First Bill',
            'view_type':'form',
            'view_mode':'tree',
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice',
            'views' : [(view_id,'form')],
            'view_id': view_id,
            'target': 'current',
            'context': {'default_boq_ref_id':self.id, 'default_project_id':self.name_of_work.id, 'default_partner_id': self.name_of_work.partner_id.id, 'default_contractor_id': self.bidder_name.id,'default_is_first_bill':True},
        }

    
class BillOfQuantityLine(models.Model):
    _name = 'bill.of.quantity.line'

    @api.one
    @api.depends('quantity','estimated_rate','revised_rate')
    def _compute_untaxed_amt(self):
        if self.revised_rate:
            self.untaxed_amt = self.revised_rate * self.quantity
        else:
            self.untaxed_amt = self.estimated_rate * self.quantity

    sl_no = fields.Char(string="Sl No.")
    line_id = fields.Many2one('bill.of.quantity')
    extra_line_id = fields.Many2one('bill.of.quantity') 
    product_id = fields.Many2one('product.product',string="Item Description")
    quantity = fields.Float(string="Quantity")
    uom_id = fields.Many2one('product.uom',string="Units")
    estimated_rate = fields.Float(string="Estimated Rate")
    untaxed_amt = fields.Float(string="Total Amount Without Tax", compute='_compute_untaxed_amt')
    amt_in_words = fields.Text(string='Total Amount In Words',store=False, readonly=True, compute='_amount_in_words')
    categ_id = fields.Many2one('product.category',string="Product Category")
    category = fields.Char(string="Category")
    product = fields.Char(string="Product")
    
    already_done_ids = fields.One2many('product.boq.line','boq_id1')
    to_be_done_ids = fields.One2many('product.boq.line','boq_id2')

    already_done_steel_ids = fields.One2many('steel.product.boq','re_id1')
    to_be_done_steel_ids = fields.One2many('steel.product.boq','re_id2')

    #For comparative statement
    already_executed_qty = fields.Float(string="Already Executed Qty", compute='_compute_already_executed')
    to_be_executed_qty = fields.Float(string="To Be Executed Qty", compute='_compute_to_be_executed')
    total_quantity = fields.Float(string="Total Quantity", compute="_compute_total_quantity")
    revised_rate = fields.Float(string="Revised Rate", compute="_compute_revised_rate")
    already_executed_revised = fields.Float(string="Already Executed Revised", compute="_compute_execute_amt")
    to_be_executed_revised = fields.Float(string="To Be Executed Revised", compute="_compute_to_execute_amt")
    revised_total = fields.Float(string="Revised Total", compute="_compute_revised_total")
    savings = fields.Float(string="Savings(Minus) in Rs" , readonly=True, compute='_compute_amount')
    excess = fields.Float(string="Excess(Plus) in Rs" , readonly=True, compute='_compute_amount')
    explanation = fields.Text(string="Explanation")
    remarks_ksrrda = fields.Text(string="Remarks of KSRRDA")
    remarks_se = fields.Text(string="Remarks of SE")
    extra_rate = fields.Float(string="Extra Revised Rate")
    # test = fields.Boolean('Test')

    @api.multi
    @api.depends('already_done_ids')
    def _compute_already_executed(self):
        for rec in self:
            for val in rec.already_done_ids:
                rec.already_executed_qty += val.qty

    @api.multi
    @api.depends('to_be_done_ids')
    def _compute_to_be_executed(self):
        for rec in self:
            for val in rec.to_be_done_ids:
                rec.to_be_executed_qty += val.qty

    @api.multi
    @api.depends('already_executed_qty','to_be_executed_qty')
    def _compute_total_quantity(self):
        for rec in self:
            rec.total_quantity = rec.already_executed_qty + rec.to_be_executed_qty


    @api.multi
    @api.depends('estimated_rate','extra_rate')
    def _compute_revised_rate(self):
        for rec in self:
            if rec.extra_rate > 0:
                rec.revised_rate = rec.extra_rate
            else:
                rec.revised_rate = rec.estimated_rate


    @api.multi
    @api.depends('already_executed_qty','revised_rate')
    def _compute_execute_amt(self):
        for rec in self:
            rec.already_executed_revised = rec.already_executed_qty * rec.revised_rate


    @api.multi
    @api.depends('to_be_executed_qty','revised_rate')
    def _compute_to_execute_amt(self):
        for rec in self:
            rec.to_be_executed_revised = rec.to_be_executed_qty * rec.revised_rate

    
    @api.multi
    @api.depends('already_executed_revised','to_be_executed_revised')
    def _compute_revised_total(self):
        for rec in self:
            rec.revised_total = rec.already_executed_revised + rec.to_be_executed_revised
    

    @api.multi
    @api.depends('untaxed_amt', 'revised_total')
    def _compute_amount(self):
        for rec in self:
            amount = rec.untaxed_amt - rec.revised_total
            if amount >= 0:
                rec.savings = amount
            if amount < 0:
                rec.excess = abs(amount)

    
    @api.model
    def create(self, vals):
        category_id = False
        product_id = False
    
        #Category
        if vals.get('category'):
            category_id = self.env['product.category'].search([('name','=',vals.get('category'))]).id
            if not category_id:
                category_id = self.env['product.category'].create({'name':vals.get('category')}).id
        vals['categ_id'] = category_id

        #Product
        if vals.get('product'):
            product_id = self.env['product.product'].search([('name','=',vals.get('product'))]).id
            # print "============================1",product_id
            if not product_id:
                for product in self.env['product.product'].search([]):
                    if vals.get('product').lower() == product.name.lower() or vals.get('product').lower().replace(" ", "") == product.name.lower().replace(" ", ""):
                        product_id = product.id
                if not product_id:
                    product_id = self.env['product.product'].create({'name':vals.get('product'),
                                                                'categ_id':category_id,
                                                                'is_boq':True}).id
            vals['product_id'] = product_id
        
        result = super(BillOfQuantityLine, self).create(vals)           
        return result
        
    @api.one
    @api.depends('untaxed_amt')
    def _amount_in_words(self):
        wGenerator = Number2Words()
        if self.untaxed_amt >= 0.0: 
            # print 'cash===================', self.untaxed_amt
            self.amt_in_words = wGenerator.convertNumberToWords(self.untaxed_amt)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_boq = fields.Boolean(string="Is BOQ")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_boq = fields.Boolean(string="Is BOQ")

class ProductBoqLine(models.Model):
    _name = 'product.boq.line'
    # _parent_order = 'type_id'
    # _order = 'type_id'
    _order = "type_id, name asc"

    # def _compute_seq(self):
    #     a = 1
    #     for val in self:
    #         val.seq = a
    #         a += 1          

    invoice_id = fields.Many2one('account.invoice')
    account_id = fields.Many2one('account.invoice.line')
    boq_id1 = fields.Many2one('bill.of.quantity.line')
    boq_id2 = fields.Many2one('bill.of.quantity.line')
    name = fields.Char(string="Description")
    no = fields.Integer(string="No.")
    type_id = fields.Many2one('item.type', string="Type")
    is_duplicate = fields.Boolean(string="Duplicate")

    l_char = fields.Char(string="L Char")
    l = fields.Char(string="L", store=True, readonly=True, compute='compute_l')
    l_avg = fields.Float(string="L Avg", store=True, readonly=True, compute='compute_l')

    b_char = fields.Char(string="B Char")
    b = fields.Char(string="B", store=True, readonly=True, compute='compute_b')
    b_avg = fields.Float(string="B Avg", store=True, readonly=True, compute='compute_b')

    d_char = fields.Char(string="D Char")
    d = fields.Char(string="D", store=True, readonly=True, compute='compute_d')
    d_avg = fields.Float(string="D Avg", store=True, readonly=True, compute='compute_d')

    b1 = fields.Float(string="B1")
    b2 = fields.Float(string="B2")
    b3 = fields.Float(string="B3")

    avg = fields.Float(string="Average",store=True, readonly=True, compute='_compute_avg')
    # d = fields.Float(string="D")
    qty = fields.Float(string="Quantity",store=True, readonly=True, compute='_compute_qty')


    @api.multi
    def unlink(self):
        return super(ProductBoqLine, self).unlink()

    # @api.multi
    # def split_quantities(self):
    #     for det in self:
    #         new_id = det.copy(context=self.env.context)
    #         # new_id.seq +=1
    #     if self and self[0]:
    #         return self[0].account_id.wizard_view()
 

    @api.one
    @api.depends('l_char')
    def compute_l(self):
        if self.l_char:
            temp = []
            array = (self.l_char).split('+')
            num_array = [float(num_string) for num_string in array]
            arr_len = len(array)
            precision = 2 
            total = 0.0
            if arr_len == 1:
                num = "{:.{}f}".format( num_array[0], precision )
                # print "=================11",num_array
                self.l = num
                # print "=================22",self.l,asd
            else:
                for val in num_array:
                    res = "{:.{}f}".format( val, precision )
                    temp.append(res)
                temp1 = '+'.join(map(str, temp)) 

                self.l = '('+str(temp1)+')'+'/'+str(arr_len)
            for val in num_array:
                total += val
            avg = (float(total)/arr_len)
            self.l_avg = "{:.{}f}".format( avg, precision )

            
    @api.one
    @api.depends('b_char')
    def compute_b(self):
        if self.b_char:
            temp = []
            array = (self.b_char).split('+')
            num_array = [float(num_string) for num_string in array]
            arr_len = len(array)
            precision = 2 
            total = 0.0
            if arr_len == 1:
                num = "{:.{}f}".format( num_array[0], precision )
                self.b = num
            else:
                for val in num_array:
                    res = "{:.{}f}".format( val, precision )
                    temp.append(res)
                temp1 = '+'.join(map(str, temp)) 

                self.b = '('+str(temp1)+')'+'/'+str(arr_len)
            for val in num_array:
                total += val
            avg = (float(total)/arr_len)
            self.b_avg = "{:.{}f}".format( avg, precision )

    @api.one
    @api.depends('d_char')
    def compute_d(self):
        if self.d_char:
            temp = []
            array = (self.d_char).split('+')
            num_array = [float(num_string) for num_string in array]
            arr_len = len(array)
            precision = 2 
            total = 0.0
            if arr_len == 1:
                num = "{:.{}f}".format( num_array[0], precision )
                self.d = num
            else:
                for val in num_array:
                    res = "{:.{}f}".format( val, precision )
                    temp.append(res)
                temp1 = '+'.join(map(str, temp)) 

                self.d = '('+str(temp1)+')'+'/'+str(arr_len)
            for val in num_array:
                total += val
            avg = (float(total)/arr_len)
            self.d_avg = "{:.{}f}".format( avg, precision )
            

    @api.one
    @api.depends('no', 'l_avg', 'b_avg', 'd_avg')
    def _compute_qty(self):
        l_avg = 0
        b_avg = 0
        d_avg = 0
        if self.l_avg == 0:
            l_avg = 1
        else:
            l_avg = self.l_avg  
        if self.b_avg == 0:
            b_avg = 1
        else:
            b_avg = self.b_avg
        if self.d_avg == 0:
            d_avg = 1
        else:
            d_avg = self.d_avg
        self.qty = self.no*l_avg*b_avg*d_avg


    # @api.multi
    # def line_duplicate_button(self):
    #   # product = self.search([('is_duplicate','=',True)])
    #   # if not product:
    #   #   raise UserError('Please select the records to duplicate')

    #   # for val in product:
            
    #   self.env['product.boq.line'].create({
    #                                   'account_id': val.account_id.id,
    #                                   'type_id':val.type_id,
    #                                   'no': val.no,
    #                                   'l_char': val.l_char,
    #                                   'l':val.l,
    #                                   'l_avg':val.l_avg,
    #                                   'b_char':val.b_char,
    #                                   'b':val.b,
    #                                   'b_avg':val.b_avg,
    #                                   'd_char':val.d_char,
    #                                   'd': val.d,
    #                                   'd_avg':val.d_avg,
    #                                   'qty': val.qty,
    #                                   })

        


    @api.one
    @api.depends('b1', 'b2', 'b3')
    def _compute_avg(self):
        if self.b1 > 0 and self.b2 > 0 and self.b3 > 0:
            self.avg = (self.b1+self.b2+self.b3)/3
        elif (self.b1 > 0 and self.b2 > 0) or (self.b2 > 0 and self.b3 > 0) or (self.b1 > 0 and self.b3 > 0):
            self.avg = (self.b1+self.b2+self.b3)/2
        else:
            self.avg = (self.b1+self.b2+self.b3)


class account_invoice(models.Model):
    _inherit = "account.invoice"

    bill_name = fields.Char(string="Bill Name")
    number = fields.Char(string="Invoice No.")
    # account_invoice_ids = fields.Many2one('account.invoice','Invoice no',required=False)
    boq_ref_id = fields.Many2one('bill.of.quantity',string="BOQ")
    parent_id = fields.Many2one('account.invoice', string="First Bill")
    status1 = fields.Selection([('draft', "Draft"), 
                                ('confirm', "Confirmed"), 
                                ('second_bill', "Generate AE Approval Bill"), 
                                ('approve', "Approved"),
                                ('update', "Updated"),
                                ('axe_approve',"Approved by AXE"),
                                ('ee_approve',"Approved by EE")],
                                string="Status", required=True, default='draft')
    is_first_bill = fields.Boolean(string="First Bill")
    is_second_bill = fields.Boolean(string="Approved First Bill")
    deduction_ids = fields.One2many('bill.deductions','invoice_id')
    status_ids = fields.One2many('bill.status','invoice_no')

    #For Deductions
    apac = fields.Float(string="APAC", compute='_compute_apac')
    contract_amt = fields.Float(string="Contract Amount", compute='_compute_contract_amt')  
    deduction = fields.Float(string="Deduction", compute='_compute_deduction')  
    balance = fields.Float(string="Balance", compute='_compute_balance')
    check_amt = fields.Float(string="Check Amount", compute='_compute_check_amt')


    @api.model
    def create(self, vals): 
        result = super(account_invoice, self).create(vals)          
        if result.number == False:
            result.number = self.env['ir.sequence'].next_by_code('account.invoice.new12') or '/'
        return result


    @api.multi
    @api.depends('project_id')
    def _compute_apac(self):
        for rec in self:
            rec.apac = rec.project_id.tender_id.apac 


    @api.multi
    @api.depends('amount_total','deduction')
    def _compute_check_amt(self):
        for rec in self:
            rec.check_amt = rec.amount_total - rec.deduction 

    @api.multi
    @api.depends('amount_total')
    def _compute_contract_amt(self):
        for rec in self:
            rec.contract_amt = rec.amount_total 

    @api.multi
    @api.depends('deduction_ids.amount')
    def _compute_deduction(self):
        for record in self:
            for val in record.deduction_ids:
                record.deduction += val.amount
    

    @api.multi
    @api.depends('apac','contract_amt')
    def _compute_balance(self):
        for rec in self:
            rec.balance = rec.apac - rec.contract_amt


    @api.model
    def default_get(self, vals):    
        res = super(account_invoice, self).default_get(vals)    
        # print 'res==========================', res
        invoice = self.env['account.invoice'].browse(self.env.context.get('default_parent_id'))
        # print 'd===========================', invoice
        if invoice:
            invoice.update({'status1':'second_bill'})                   
            invoice_ids = []

            
            for rec in invoice.invoice_line:
                tax_ids = []
                for tax in rec.invoice_line_tax_id:
                    tax_ids.append(tax.id)
                # print 'rec==============', rec
                product_boq = []
                steel_boq = []
                for line in rec.boq_ids:
                    product_boq.append((0, 0, { 'name':line.name,
                                                'type_id':line.type_id.id,
                                                'no':line.no,                                                       
                                                'l_char':line.l_char,
                                                'l':line.l,
                                                'l_avg':line.l_avg,
                                                'b_char':line.b_char,
                                                'b':line.b,
                                                'b_avg':line.b_avg,
                                                'd_char':line.d_char,
                                                'd':line.d,
                                                'd_avg':line.d_avg,
                                                # 'b1':line.b1,
                                                # 'b2':line.b2,
                                                # 'b3':line.b3,
                                                # 'avg':line.avg,
                                                # 'd':line.d,
                                                'qty':line.qty,
                                          }))
                for val in rec.steel_ids:
                    steel_boq.append((0, 0, {   'name':val.name,
                                                'diameter':val.diameter.id,
                                                'no':val.no,                                                        
                                                'length':val.length,
                                                'qty_in_meter':val.qty_in_meter,
                                                'qty':val.qty,
                                                
                                          }))
                # raise UserError(str(rec.invoice_line_tax_id.id))

                invoice_ids.append((0, 0, { 'product_id':rec.product_id.id,
                                            'name': rec.name,
                                            'account_id':rec.account_id.id,
                                            'quantity':rec.quantity,
                                            'uos_id':rec.uos_id.id,
                                            'price_unit':rec.price_unit,
                                            'invoice_line_tax_id':[(6,0,tax_ids)],
                                            'price_subtotal':rec.price_subtotal,
                                            'boq_ids':product_boq,
                                            'steel_ids':steel_boq,
                                          }))
    
        
            res.update({'invoice_line': invoice_ids})
        # print 'res===================', res
        return res

    @api.multi
    def button_confirm(self):
        return self.write({'status1': 'confirm'
                            })

    @api.multi
    def button_confirm_update(self):        
        for inv in self:            
            boq = self.env['bill.of.quantity'].search([('id','=',inv.boq_ref_id.id)]).id
            if boq:
                for val in inv.invoice_line:

                    line_id = self.env['bill.of.quantity.line'].search([('product_id','=',val.product_id.id),'|',('line_id','=',boq),('extra_line_id','=',boq)], limit=1)
                    
                    for value in val.boq_ids:
                        self.env['product.boq.line'].create({
                                                        'name':value.name,
                                                        'type_id':value.type_id.id,
                                                        'no':value.no,
                                                        'l_char':value.l_char,                                                      
                                                        'l':value.l,
                                                        'l_avg':value.l_avg,
                                                        'b_char':value.b_char,
                                                        'b':value.b,
                                                        'b_avg':value.b_avg,
                                                        'd_char':value.d_char,
                                                        'd':value.d,
                                                        'd_avg':value.d_avg,
                                                        'qty':value.qty,
                                                        'boq_id2':line_id.id,
                                                        'invoice_id':inv.id                                                         

                                                        })
                    for vals in val.steel_ids:
                        self.env['steel.product.boq'].create({
                                                            'diameter':vals.diameter.id,
                                                            'name':vals.name,
                                                            'no':vals.no,
                                                            'length':vals.length,
                                                            'qty_in_meter':vals.qty_in_meter,
                                                            'qty':vals.qty,
                                                            're_id2':line_id.id,
                                                            'invoice_id':inv.id                                                         
        
                                                            })
                    
                    if not line_id:
                        to_be_done_ids = []
                        to_be_done_steel_ids = []
                        values = {}
                        for value in val.boq_ids:
                            values = {
                                        'name':value.name,
                                        'type_id':value.type_id.id,
                                        'no':value.no,                                                      
                                        'l_char':value.l_char,                                                      
                                        'l':value.l,
                                        'l_avg':value.l_avg,
                                        'b_char':value.b_char,
                                        'b':value.b,
                                        'b_avg':value.b_avg,
                                        'd_char':value.d_char,
                                        'd':value.d,
                                        'd_avg':value.d_avg,                                        
                                        'qty':value.qty,
                                        'boq_id2':line_id.id,
                                        'invoice_id':inv.id                                                         

                                        }

                            pro_boq = self.env['product.boq.line'].create(values)
                            to_be_done_ids.append(pro_boq.id)

                        for vals in val.steel_ids:
                            steel_pro_id = self.env['steel.product.boq'].create({
                                                            'diameter':vals.diameter.id,
                                                            'name':vals.name,
                                                            'no':vals.no,
                                                            'length':vals.length,
                                                            'qty_in_meter':vals.qty_in_meter,
                                                            'qty':vals.qty,
                                                            're_id2':line_id.id,
                                                            'invoice_id':inv.id                                                         

                                                            })
                            to_be_done_steel_ids.append(steel_pro_id.id)

                        self.env['bill.of.quantity.line'].create({
                                                    'product_id':val.product_id.id,
                                                    'uom_id':val.uos_id.id,
                                                    'extra_rate':val.price_unit,
                                                    'extra_line_id':boq,
                                                    'to_be_done_ids':[(6, 0, to_be_done_ids)],
                                                    'to_be_done_steel_ids':[(6, 0, to_be_done_steel_ids)],
            
                                                })
            inv.update({
                        'status1':'confirm',
                        })


    @api.multi
    def button_update_already_done(self):       
        for inv in self:
            boq = self.env['bill.of.quantity'].search([('id','=',inv.boq_ref_id.id)]).id
            if boq:
                for val in inv.invoice_line:
                    line_id = self.env['bill.of.quantity.line'].search([('product_id','=',val.product_id.id),'|',('line_id','=',boq),('extra_line_id','=',boq)], limit=1)
                    
                    for value in val.boq_ids:
                        self.env['product.boq.line'].create({
                                                        'name':value.name,
                                                        'type_id':value.type_id.id,
                                                        'no':value.no,
                                                        'l_char':value.l_char,                                                      
                                                        'l':value.l,
                                                        'l_avg':value.l_avg,
                                                        'b_char':value.b_char,
                                                        'b':value.b,
                                                        'b_avg':value.b_avg,
                                                        'd_char':value.d_char,
                                                        'd':value.d,
                                                        'd_avg':value.d_avg,
                                                        'qty':value.qty,
                                                        'boq_id1':line_id.id,
                                                        'invoice_id':inv.id,                                                        
                                                        })
                    for vals in val.steel_ids:
                        self.env['steel.product.boq'].create({
                                                            'diameter':vals.diameter.id,
                                                            'name':vals.name,
                                                            'no':vals.no,
                                                            'length':vals.length,
                                                            'qty_in_meter':vals.qty_in_meter,
                                                            'qty':vals.qty,
                                                            're_id1':line_id.id,
                                                            'invoice_id':inv.id
                                                            })
                    
                    if not line_id:             
                        already_done_ids = []
                        already_done_steel_ids = []
                        values = {}
                        for value in val.boq_ids:
                            values = {
                                        'name':value.name,
                                        'type_id':value.type_id.id,
                                        'no':value.no,                                                      
                                        'l_char':value.l_char,                                                      
                                        'l':value.l,
                                        'l_avg':value.l_avg,
                                        'b_char':value.b_char,
                                        'b':value.b,
                                        'b_avg':value.b_avg,
                                        'd_char':value.d_char,
                                        'd':value.d,
                                        'd_avg':value.d_avg,
                                        'qty':value.qty,
                                        'boq_id1':line_id.id,
                                        'invoice_id':inv.id,#newly added
                                        }

                            pro_boq = self.env['product.boq.line'].create(values)
                            already_done_ids.append(pro_boq.id)

                        for vals in val.steel_ids:
                            steel_pro_id = self.env['steel.product.boq'].create({
                                                            'diameter':vals.diameter.id,
                                                            'name':vals.name,
                                                            'no':vals.no,
                                                            'length':vals.length,
                                                            'qty_in_meter':vals.qty_in_meter,
                                                            'qty':vals.qty,
                                                            're_id1':line_id.id,
                                                            'invoice_id':inv.id                                                         
                                                            })
                            already_done_steel_ids.append(steel_pro_id.id)

                        self.env['bill.of.quantity.line'].create({
                                                    'product_id':val.product_id.id,
                                                    'uom_id':val.uos_id.id,
                                                    'extra_rate':val.price_unit,
                                                    'extra_line_id':boq,
                                                    'already_done_ids':[(6, 0, already_done_ids)],
                                                    'already_done_steel_ids':[(6, 0, already_done_steel_ids)],
            
                                                })
            inv.update({
                        'status1':'confirm',
                        })



    @api.multi
    def approve_button(self):
        return self.write({'status1': 'approve'
                            })

    @api.multi
    def axe_approve_button(self):
        return self.write({'status1': 'axe_approve'
                            })

    @api.multi
    def ee_approve_button(self):
        return self.write({'status1': 'ee_approve'
                            })

    
    @api.multi
    def view_first_bill(self):
        view_id = self.env.ref('hiworth_boq.first_bill_invoice_form_123').id
        return{
            'name': 'First Bill',
            'view_type':'form',
            'views' : [(view_id,'form')],
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice',
            'res_id': self.parent_id.id,
            }

        
    @api.multi
    def generate_second_bill(self):
        view_id = self.env.ref('hiworth_boq.second_bill_invoice_form_123').id
        return{
            'name': 'Approved First Bill',
            'view_type':'form',
            'view_mode':'tree',
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice',
            'views' : [(view_id,'form')],
            'view_id': view_id,
            'target' : 'current',
            'context': {'default_boq_ref_id':self.boq_ref_id.id, 'default_project_id':self.project_id.id, 'default_bill_name':self.bill_name,
                        'default_partner_id': self.partner_id.id, 'default_contractor_id': self.contractor_id.id, 'default_parent_id':self.id, 'default_date_invoice': self.date_invoice,
                        'default_status1':'second_bill', 'default_is_second_bill': True, 'default_account_id':self.account_id.id,}
        }


    @api.multi
    def action_update_re(self):
        for inv in self:            
            boq = self.env['bill.of.quantity'].search([('id','=',inv.boq_ref_id.id)]).id
            if boq:
                for val in inv.invoice_line:
                    line_id = self.env['bill.of.quantity.line'].search([('product_id','=',val.product_id.id),'|',('line_id','=',boq),('extra_line_id','=',boq)], limit=1)
                    boq_line = self.env['product.boq.line'].search(['|',('boq_id2','=',line_id.id),('boq_id1','=',line_id.id),('invoice_id','=',inv.parent_id.id)])
                    for line in boq_line:
                        line.unlink()
                    steel_line = self.env['steel.product.boq'].search(['|',('re_id2','=',line_id.id),('re_id1','=',line_id.id),('invoice_id','=',inv.parent_id.id)])
                    for line2 in steel_line:                        
                        line2.unlink()
                    for value in val.boq_ids:
                        self.env['product.boq.line'].create({
                                                        'name':value.name,
                                                        'type_id':value.type_id.id,
                                                        'no':value.no,                                                      
                                                        'l_char':value.l_char,
                                                        'l':value.l,
                                                        'l_avg':value.l_avg,
                                                        'b_char':value.b_char,
                                                        'b':value.b,
                                                        'b_avg':value.b_avg,
                                                        'd_char':value.d_char,
                                                        'd':value.d,
                                                        'd_avg':value.d_avg,
                                                        'qty':value.qty,
                                                        'boq_id1':line_id.id,
                                                        'account_id':val.id,
                                                        'invoice_id':inv.id                                                         

                                                        })
                    for vals in val.steel_ids:
                        self.env['steel.product.boq'].create({
                                                            'diameter':vals.diameter.id,
                                                            'name':vals.name,
                                                            'no':vals.no,
                                                            'length':vals.length,
                                                            'qty_in_meter':vals.qty_in_meter,
                                                            'qty':vals.qty,
                                                            're_id1':line_id.id,
                                                            'invoice_id':inv.id                                                         

                                                            })
                    if not line_id:                 
                        already_done_ids = []
                        already_done_steel_ids = []
                        values = {}
                        for value in val.boq_ids:
                            values = {
                                        'name':value.name,
                                        'type_id':value.type_id.id,
                                        'no':value.no,                                                      
                                        'l_char':value.l_char,
                                        'l':value.l,
                                        'l_avg':value.l_avg,
                                        'b_char':value.b_char,
                                        'b':value.b,
                                        'b_avg':value.b_avg,
                                        'd_char':value.d_char,
                                        'd':value.d,
                                        'd_avg':value.d_avg,
                                        'qty':value.qty,
                                        'boq_id1':line_id.id,
                                        'invoice_id':inv.id                                                         

                                    }

                            pro_boq = self.env['product.boq.line'].create(values)
                            already_done_ids.append(pro_boq.id)

                        for vals in val.steel_ids:
                            steel_pro_id = self.env['steel.product.boq'].create({
                                                            'diameter':vals.diameter.id,
                                                            'name':vals.name,
                                                            'no':vals.no,
                                                            'length':vals.length,
                                                            'qty_in_meter':vals.qty_in_meter,
                                                            'qty':vals.qty,
                                                            're_id1':line_id.id,
                                                            'invoice_id':inv.id                                                         

                                                            })
                            already_done_steel_ids.append(steel_pro_id.id)


                        self.env['bill.of.quantity.line'].create({
                                                    'product_id':val.product_id.id,
                                                    'uom_id':val.uos_id.id,
                                                    'extra_rate':val.price_unit,
                                                    'extra_line_id':boq,
                                                    'already_done_ids':[(6, 0, already_done_ids)],
                                                    'already_done_steel_ids':[(6, 0, already_done_steel_ids)],
                                                })
                    
                inv.update({
                            'status1':'update',
                            })


    @api.multi
    def unlink(self):
        return super(account_invoice, self).unlink()

    @api.multi
    def action_update_to_be_done(self):
        for inv in self:            
            boq = self.env['bill.of.quantity'].search([('id','=',inv.boq_ref_id.id)]).id    
            if boq:             
                for val in inv.invoice_line:
                    line_id = self.env['bill.of.quantity.line'].search([('product_id','=',val.product_id.id),'|',('line_id','=',boq),('extra_line_id','=',boq)], limit=1)
                    boq_line = self.env['product.boq.line'].search(['|',('boq_id1','=',line_id.id),('boq_id2','=',line_id.id),('invoice_id','=',inv.parent_id.id)])
                    for line in boq_line:
                        line.unlink()
                    steel_line = self.env['steel.product.boq'].search(['|',('re_id1','=',line_id.id),('re_id2','=',line_id.id),('invoice_id','=',inv.parent_id.id)])
                    for line2 in steel_line:                        
                        line2.unlink()
                    for value in val.boq_ids:
                        self.env['product.boq.line'].create({
                                                        'name':value.name,
                                                        'type_id':value.type_id.id,
                                                        'no':value.no,                                                      
                                                        'l_char':value.l_char,
                                                        'l':value.l,
                                                        'l_avg':value.l_avg,
                                                        'b_char':value.b_char,
                                                        'b':value.b,
                                                        'b_avg':value.b_avg,
                                                        'd_char':value.d_char,
                                                        'd':value.d,
                                                        'd_avg':value.d_avg,
                                                        'qty':value.qty,
                                                        'boq_id2':line_id.id,
                                                        'account_id':val.id,
                                                        'invoice_id':inv.id,#newly added
                                                        })
                    for vals in val.steel_ids:
                        self.env['steel.product.boq'].create({
                                                            'diameter':vals.diameter.id,
                                                            'name':vals.name,
                                                            'no':vals.no,
                                                            'length':vals.length,
                                                            'qty_in_meter':vals.qty_in_meter,
                                                            'qty':vals.qty,
                                                            're_id2':line_id.id,
                                                            'invoice_id':inv.id                                                         
                                                            })
                    if not line_id:                 
                        to_be_done_ids = []
                        to_be_done_steel_ids = []
                        values = {}
                        for value in val.boq_ids:
                            values = {
                                        'name':value.name,
                                        'type_id':value.type_id.id,
                                        'no':value.no,                                                      
                                        'l_char':value.l_char,
                                        'l':value.l,
                                        'l_avg':value.l_avg,
                                        'b_char':value.b_char,
                                        'b':value.b,
                                        'b_avg':value.b_avg,
                                        'd_char':value.d_char,
                                        'd':value.d,
                                        'd_avg':value.d_avg,
                                        'qty':value.qty,
                                        'boq_id2':line_id.id,
                                        'invoice_id':inv.id,

                                        }

                            pro_boq = self.env['product.boq.line'].create(values)
                            to_be_done_ids.append(pro_boq.id)

                        for vals in val.steel_ids:
                            steel_pro_id = self.env['steel.product.boq'].create({
                                                            'diameter':vals.diameter.id,
                                                            'name':vals.name,
                                                            'no':vals.no,
                                                            'length':vals.length,
                                                            'qty_in_meter':vals.qty_in_meter,
                                                            'qty':vals.qty,
                                                            're_id2':line_id.id,
                                                            'invoice_id':inv.id
                                                            })
                            to_be_done_steel_ids.append(steel_pro_id.id)


                        self.env['bill.of.quantity.line'].create({
                                                    'product_id':val.product_id.id,
                                                    'uom_id':val.uos_id.id,
                                                    'extra_rate':val.price_unit,
                                                    'extra_line_id':boq,
                                                    'to_be_done_ids':[(6, 0, to_be_done_ids)],
                                                    'to_be_done_steel_ids':[(6, 0, to_be_done_steel_ids)],
                                                })
                    
                inv.update({
                            'status1':'update',
                            })


    #validate button
    # @api.multi
    # def action_move_create(self):
    #   for inv in self:
            
    #       boq = self.env['bill.of.quantity'].search([('id','=',inv.boq_ref_id.id)]).id
    #       if boq:
    #           for val in inv.invoice_line:
    #               line_id = self.env['bill.of.quantity.line'].search([('product_id','=',val.product_id.id),('line_id','=',boq)], limit=1)
    #               for value in val.boq_ids:
    #                   self.env['product.boq.line'].create({
    #                                                   'name':value.name,
    #                                                   'no':value.no,                                                      
    #                                                   'l':value.l,
    #                                                   'b1':value.b1,
    #                                                   'b2':value.b2,
    #                                                   'b3':value.b3,
    #                                                   'avg':value.avg,
    #                                                   'd':value.d,
    #                                                   'qty':value.qty,
    #                                                   'boq_id':line_id.id
    #                                                   })
    #   return super(account_invoice, self).action_move_create()


    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_invoice_tax = self.env['account.invoice.tax']
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise except_orm(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise except_orm(_('No Invoice Lines!'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            company_currency = inv.company_id.currency_id
            if not inv.date_invoice:
                # FORWARD-PORT UP TO SAAS-6
                if inv.currency_id != company_currency and inv.tax_line:
                    raise except_orm(
                        _('Warning!'),
                        _('No invoice date!'
                            '\nThe invoice currency is not the same than the company currency.'
                            ' An invoice date is required to determine the exchange rate to apply. Do not forget to update the taxes!'
                        )
                    )
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            date_invoice = inv.date_invoice

            # create the analytical lines, one move line per invoice line
            iml = inv._get_analytic_lines()
            # check if taxes are all computed
            compute_taxes = account_invoice_tax.compute(inv.with_context(lang=inv.partner_id.lang))
            inv.check_tax_lines(compute_taxes)

            # I disabled the check_total feature
            if self.env.user.has_group('account.group_supplier_inv_check_total'):
                if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding / 2.0):
                    raise except_orm(_('Bad Total!'), _('Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))

            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise except_orm(_('Error!'), _("Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))

            # Force recomputation of tax_amount, since the rate potentially changed between creation
            # and validation of the invoice
            inv._recompute_tax_amount()
            # one move line per tax line
            iml += account_invoice_tax.move_line_get(inv.id)

            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
            else:
                ref = inv.number

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, ref, iml)

            name = inv.supplier_invoice_number or inv.name or '/'
            totlines = []
            if inv.payment_term:
                totlines = inv.with_context(ctx).payment_term.compute(total, date_invoice)[0]
            if totlines:
                res_amount_currency = total_currency
                ctx['date'] = date_invoice
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'ref': ref,
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'ref': ref
                })

            date = date_invoice

            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)

            line = [(0, 0, self.line_get_convert(l, part.id, date)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            if journal.centralisation:
                raise except_orm(_('User Error!'),
                        _('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

            line = inv.finalize_invoice_move_lines(line)

            move_vals = {
                'ref': inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal.id,
                'date': inv.date_invoice,
                'narration': inv.comment,
                'company_id': inv.company_id.id,
            }
            ctx['company_id'] = inv.company_id.id
            period = inv.period_id
            if not period:
                period = period.with_context(ctx).find(date_invoice)[:1]
            if period:
                move_vals['period_id'] = period.id
                for i in line:
                    i[2]['period_id'] = period.id

            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            temp = inv.number
            move = account_move.with_context(ctx_nolang).create(move_vals)

            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'period_id': period.id,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
            inv.number =  temp
        self._log_event()
        return True

    @api.multi
    def action_cancel(self):
        moves = self.env['account.move']
        for inv in self:
            boq = self.env['bill.of.quantity'].search([('id','=',inv.boq_ref_id.id)]).id
            if boq:
                for val in inv.invoice_line:
                    line_id = self.env['bill.of.quantity.line'].search([('product_id','=',val.product_id.id),('line_id','=',boq)], limit=1)
                    obj = self.env['product.boq.line'].search([('boq_id1','=',line_id.id)])
                    for record in obj:
                        record.unlink()
                
            if inv.move_id:
                moves += inv.move_id
            if inv.payment_ids:
                for move_line in inv.payment_ids:
                    if move_line.reconcile_partial_id.line_partial_ids:
                        raise except_orm(_('Error!'), _('You cannot cancel an invoice which is partially paid. You need to unreconcile related payment entries first.'))

        # First, set the invoices as cancelled and detach the move ids
        self.write({'state': 'cancel', 'move_id': False})
        if moves:
            # second, invalidate the move(s)
            moves.button_cancel()
            # delete the move this invoice was pointing to
            # Note that the corresponding move_lines and move_reconciles
            # will be automatically deleted too
            moves.unlink()
        self._log_event(-1.0, 'Cancel Invoice')
        return True


class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"

    boq_ids = fields.One2many('product.boq.line','account_id')
    steel_ids = fields.One2many('steel.product.boq','inv_id')
    search_product_id = fields.Many2one('product.product',string="Select Product")
    sl_no = fields.Char(string="Sl No.")

    # @api.multi
    # def wizard_view(self):
    #     view = self.env.ref('account.view_invoice_line_form')

    #     return {
    #         'name': _('product boq line'),
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'account.invoice.line',
    #         'views': [(view.id, 'form')],
    #         'view_id': view.id,
    #         'target': 'new',
    #         'res_id': self.ids[0],
    #         'context': self.env.context,
    #     }


    # @api.model
    # def create(self, vals): 
    #     result = super(account_invoice_line, self).create(vals)
        
    #     a = 1
    #     # raise UserError(vals)
    #     for val in vals['boq_ids']:
    #         # raise UserError(type(val[2]))
    #         if val[2]['seq'] == 0:
    #             val[2]['seq'] = a
    #             # raise UserError(val[0])
    #             a += 1          

    #     return result

    @api.onchange('search_product_id')
    def onchange_search_product(self):  
        product_ids = []
        res = {}
        if self.invoice_id.project_id.id != False:
            boq = self.env['bill.of.quantity'].search([('name_of_work','=',self.invoice_id.project_id.id),('id','=',self.invoice_id.boq_ref_id.id)])
            for val in boq:
                order_lines = self.env['bill.of.quantity.line'].search(['|',('line_id','=',val.id),('extra_line_id','=',val.id)])

                product_ids = [order_line.product_id.id for order_line in order_lines]
                res['domain'] = {'search_product_id': [('id','in',product_ids)]}

        
        line_ids = []
        if self.search_product_id:
            product = self.env['account.invoice.line'].search([('product_id','=',self.search_product_id.id),('invoice_id','=',self.env.context.get('invoice'))])
            for prod in product.boq_ids:

                values = {   
                            'name':prod.name,
                            'type_id':prod.type_id.id,
                            'no':prod.no,                                                       
                            'l_char':prod.l_char,
                            'l':prod.l,
                            'l_avg':prod.l_avg,
                            'b_char':prod.b_char,
                            'b':prod.b,
                            'b_avg':prod.b_avg,
                            'd_char':prod.d_char,
                            'd':prod.d,
                            'd_avg':prod.d_avg,                                                     
                            'qty':prod.qty,
                        }

                line_ids.append((0, False, values ))
            self.boq_ids = line_ids
            res['boq_ids'] = {'boq_ids':line_ids}

        return res
                
            
    @api.onchange('product_id','name')
    def onchange_product_id(self):
        product_ids = []
        if self.invoice_id.project_id.id != False:
            boq = self.env['bill.of.quantity'].search([('name_of_work','=',self.invoice_id.project_id.id),('id','=',self.invoice_id.boq_ref_id.id)])
            for val in boq:
                order_lines = self.env['bill.of.quantity.line'].search(['|',('line_id','=',val.id),('extra_line_id','=',val.id)])
                product_ids = [order_line.product_id.id for order_line in order_lines]
                if self.product_id:
                    bill = order_lines.search([('product_id','=',self.product_id.id),'|',('line_id','=',val.id),('extra_line_id','=',val.id)])
                    self.sl_no = bill.sl_no
                    self.quantity = bill.quantity
                    self.uos_id = bill.uom_id.id
                    if bill.extra_rate:
                        self.price_unit = bill.extra_rate
                    else:   
                        self.price_unit = bill.estimated_rate
                return {'domain': {'product_id': [('id','in',product_ids)]}}
    
    
    @api.multi
    def line_duplicate_button(self):
        for rec in self:
            list_ids = []
            for lines in rec.boq_ids:
                if lines.id not in list_ids:
                    list_ids.append(lines.id)
            line = self.env['product.boq.line'].search([('account_id','=',rec.id),('is_duplicate','=',True)])
            values = {
                    'name':line.name,
                    'type_id':line.type_id.id,
                    'no':line.no,
                    'l_char':line.l_char,
                    'l_char':line.l_char,
                    'b_char':line.b_char,
                    'd_char':line.d_char,
                    'account_id':line.account_id.id,
            }
            new_line = self.env['product.boq.line'].create(values)
            list_ids.append(new_line.id)
            rec.write({'boq_ids':[(6, 0,list_ids )]})


class BillDeductions(models.Model):
    _name = 'bill.deductions'
    
    invoice_id = fields.Many2one('account.invoice')
    contract_amt = fields.Float(string="Contract Amount", related='invoice_id.amount_total')
    deduction_id = fields.Many2one('master.deduction',string="Deduction")
    rate = fields.Float(string="Rate")
    amount = fields.Float(string="Deduction Amount")


    @api.onchange('rate','contract_amt')
    def onchange_rate(self):
        for val in self:
            if val.rate > 0:
                val.amount = val.contract_amt * (val.rate/100)


class MasterDeduction(models.Model):
    _name = 'master.deduction'

    name = fields.Char(string="Deduction")


class BillStatus(models.Model):
    _name = 'bill.status'

    invoice_no = fields.Many2one('account.invoice',string="Invoice Number")
    date = fields.Date(string="Date", default=fields.Date.today())
    user_id = fields.Many2one('res.users', string='User', track_visibility='onchange', default=lambda self: self.env.user)
    status = fields.Text(string="Status")

class ItemType(models.Model):
    _name = 'item.type'

    name = fields.Char(string="Type")


class SteelConfig(models.Model):
    _name = 'steel.config'
    _rec_name = "diameter"

    diameter = fields.Float(string="Diameter")
    wgt_per_meter = fields.Float(string="Weight/Meter")


class SteelProductBoq(models.Model):
    _name = 'steel.product.boq'

    re_id1 = fields.Many2one('bill.of.quantity.line')
    re_id2 = fields.Many2one('bill.of.quantity.line')
    inv_id = fields.Many2one('account.invoice.line')
    invoice_id = fields.Many2one('account.invoice')
    diameter = fields.Many2one('steel.config',string="Diameter")
    name = fields.Char(string="Description")
    no = fields.Integer(string="No.")
    length = fields.Float(string="Length")
    qty_in_meter = fields.Float(string="Qty in Meter", store=False, readonly=True, compute='_compute_qty_in_mtr')
    qty = fields.Float(string="Quantity", store=False, readonly=True, compute='_compute_qty')
    
    @api.multi
    def unlink(self):
        return super(SteelProductBoq, self).unlink()

    @api.one
    @api.depends('no','length')
    def _compute_qty_in_mtr(self):
        self.qty_in_meter = self.no * self.length

    @api.one
    @api.depends('diameter','qty_in_meter')
    def _compute_qty(self):
        rate = 0.0          
        if self.diameter:
            rate = self.diameter.wgt_per_meter
            # raise UserError(rate)
        self.qty = self.qty_in_meter * rate


class product_uom(models.Model):
    _inherit = "product.uom"

    decimal_no = fields.Integer(string="Decimal point")
