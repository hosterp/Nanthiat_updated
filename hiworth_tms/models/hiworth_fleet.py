from openerp import fields, models, api
from openerp.osv import osv
from dateutil import relativedelta


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    is_insurer = fields.Boolean('Is Insurer')


class VehicleLogservices1(models.Model):
    _inherit = 'fleet.vehicle.log.services'
    
    odometer_end = fields.Float('End Value')
    start_location = fields.Char('Location From')
    dest_location = fields.Char('Location To')
    opening_bal = fields.Float('Opening Balance')
    ending_bal = fields.Float('Ending Balance')


class VehicleRouteMapping(models.Model):
    _name = 'fleet.route.mapping'

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    driver_id = fields.Many2one('hr.employee', string='Driver')
    routes = fields.One2many('fleet.route.mapping.line','route_id')
    start_bal = fields.Float('Start Balance')
    # end_bal = fields.Float('End Balance', compute="_compute_end_balance")


    @api.onchange('vehicle_id')
    def onchange_driver(self):
    	self.driver_id = self.vehicle_id.hr_driver_id.id

	# @api.multi
	# def _compute_end_balance(self):
	# 	for record in self:
	# 		bal = record.start_bal
	# 		for rec in record.routes:
	# 			bal = bal - rec.ending_bal


class VehicleRouteMapping1(models.Model):
    _name = 'fleet.route.mapping.line'

    route_id = fields.Many2one('fleet.route.mapping')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', related='route_id.vehicle_id')
    # license_plate = fields.Char('Liscense Plate', related='vehicle.license_plate')
    time_from = fields.Datetime('Start Time')
    time_to = fields.Datetime('End Time')
    driver_id = fields.Many2one('hr.employee', string='Driver', related='route_id.driver_id')
    odometer_start = fields.Float('Odometer Start Value')
    odometer_end = fields.Float('Odometer End Value')
    start_location = fields.Many2one('stock.location', string='Route From')
    dest_location = fields.Many2one('stock.location', string='Route To')
    opening_bal = fields.Float('Opening Balance')
    ending_bal = fields.Float('Ending Balance')

    stocks = fields.One2many('fleet.vehicle.stock','stock_id')

    @api.onchange('vehicle_id')
    def onchange_driver(self):
    	self.driver_id = self.vehicle_id.hr_driver_id.id

    

class VehicleRouteMapping2(models.Model):
    _name = 'fleet.vehicle.stock'

    stock_id = fields.Many2one('fleet.route.mapping.line')
    product_id = fields.Many2one('product.product', string='Product')
    description = fields.Char('Description')
    quantity = fields.Float('Quantity')



class VehicleDocuments(models.Model):
    _name = 'fleet.vehicle.documents'

    date = fields.Date('Date')
    renewal_date = fields.Date('Renewal Date')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", domain="[('rent_vehicle','!=',True)]")
    amount = fields.Float('Amount')
    journal_id = fields.Many2one('account.journal',string='Mode Of Payment', domain="[('type','in',['cash','bank'])]")
    account_id = fields.Many2one('account.account', string="Debit Account")
    insurer_id = fields.Many2one('res.partner', string="Insurance Company")
    state = fields.Selection([('draft','Draft'),('paid','Paid')], default="draft")
    document_type = fields.Selection([('pollution','Pollution'),
                                    ('road_tax','Road Tax'),
                                    ('fitness','Fitness'),
                                    ('insurance','Insurance'),
                                    ], string="Document Type")
    is_account_entry = fields.Boolean('Is Account Entry Needed?', default=True)

    @api.onchange('date')
    def onchange_renewal_date(self):
        print 'aaaaaaaaaaaaaaaaa'
        if self.date:
            print 'bbbbbbbbbbbbbbbbbb'
            date = fields.Datetime.from_string(self.date)
            print 'cccccccccccccccccccccc'
            if self.document_type == 'pollution':
                print 'DDDDDDDDDDD-------------',date,(relativedelta.relativedelta(months=6))
                self.renewal_date = date + relativedelta.relativedelta(months=6)
            elif self.document_type == 'fitness':
                self.renewal_date = date + relativedelta.relativedelta(months=12)
            elif self.document_type == 'insurance':
                self.renewal_date = date + relativedelta.relativedelta(months=12)
            else:
                pass
   

    @api.multi
    def button_payment(self):
        if self.is_account_entry == True:
            print 'z-----------------------------------------------------------'
            move = self.env['account.move']
            move_line = self.env['account.move.line']
            
                
            if self.account_id.id == False and self.journal_id.id == False:
                raise osv.except_osv(('Error'), ('Please configure journal and account for this payment'));
            elif self.account_id.id == False:
                raise osv.except_osv(('Error'), ('Please configure account for this payment'));
            elif self.journal_id.id == False:
                raise osv.except_osv(('Error'), ('Please configure journal for this payment'));
            else:
                pass

            values = {
                    'journal_id': self.journal_id.id,
                    # 'date': rec.date,
                    }
            move_id = move.create(values)

            values = {
                    'account_id': self.account_id.id,
                    'name': str(self.document_type) + 'Payment',
                    'debit': self.amount,
                    'credit': 0,
                    'move_id': move_id.id,
                    }
            line_id = move_line.create(values)

            
            values2 = {
                    'account_id': self.journal_id.default_credit_account_id.id,
                    'name': str(self.document_type) + 'Payment',
                    'debit': 0,
                    'credit': self.amount,
                    'move_id': move_id.id,
                    }
            line_id = move_line.create(values2)
            move_id.button_validate()
            self.state = 'paid'





