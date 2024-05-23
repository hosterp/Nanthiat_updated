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



class bank_emi_lines(models.Model):
    _name = 'bank.emi.lines'
    
    
    name = fields.Char('Name', size=64)
    date = fields.Date('Date')
    payment_mode = fields.Selection([('cash','Cash'),('bank','Bank'),('cheque','Cheque')], 'Mode Of Payment', select=True)
    reference = fields.Text('Reference')
    amount = fields.Float('Amount', Default=0.0)
    emi_line = fields.Many2one('fleet.vehicle', 'EMI Payment Details')
    receipt_no = fields.Char('Receipt No', size=64)
    
    
class bank_emi_lines(models.Model):
    _name = 'agent.ins.lines'
    
    
    name = fields.Char('Name', size=64)
    date = fields.Date('Date')
    payment_mode = fields.Selection([('cash','Cash'),('bank','Bank'),('cheque','Cheque')], 'Mode Of Payment', select=True)
    reference = fields.Text('Reference')
    amount = fields.Float('Amount', Default=0.0)
    ins_line = fields.Many2one('fleet.vehicle', 'Insurance Payment Details')
    receipt_no = fields.Char('Receipt No', size=64)
    
    
    
class puc_lines(models.Model):
    _name = 'puc.lines'
    
    
    name = fields.Char('Name', size=64)
    date = fields.Date('Date')
    exp_date = fields.Date('Expiry Date')
    reference = fields.Text('Reference')
    amount = fields.Float('Amount', Default=0.0)
    puc_line = fields.Many2one('fleet.vehicle', 'Insurance Payment Details')
    receipt_no = fields.Char('Receipt No', size=64)
    
    

class fleet_vehicle(models.Model):
    _inherit = 'fleet.vehicle'



    def _generate_virtual_location(self, cr, uid, truck, vehicle_ok, trailer_ok, context): 
        pass
    
    
    # def onchange_basic_odometer(self, cr, uid, ids, counter_basic, context=None):
    #     data={}
    #     if counter_basic:
    #         data['odometer'] = counter_basic
    #     return {'value' : data}

    @api.multi
    @api.depends('counter_basic','meter_lines')
    def get_odometer(self):
        for rec in self:
            if not rec.meter_lines:
                rec.odometer = rec.counter_basic
            else:
                odometers = self.env['vehicle.meter'].search([('vehicle_id','=',rec.id)], order='date desc', limit=1)
                rec.odometer = odometers.end_value

    @api.model
    def _cron_fleet_contract(self):
        prev_popups = self.env['popup.notifications'].search([('contract_pop_up', '=', True)])
        for popup in prev_popups:
            popup.unlink()

        contracts = self.env['fleet.vehicle.log.contract'].search([])
        for contra in contracts:
            if contra.expiration_date:
                expiration_date = datetime.strptime(contra.expiration_date, '%Y-%m-%d').date()
                if contra.expiration_date and abs((expiration_date - today).days) <= 1:
                    self.env['popup.notifications'].sudo().create({
                        'name': contra.vehicle_id.name,
                        'status': 'draft',
                        'message': "Contract of Accessory "+contra.vehicle_id.name,
                        'contract_pop_up': True,
                    })




    owner = fields.Many2one('res.partner', 'Owner', size=64)
    manager = fields.Many2one('res.partner', 'Manager', size=64)
    
    gasoil_id = fields.Many2one('product.product', 'Fuel', required=False, domain=[('fuel_ok','=','True')])
    
    emi_no = fields.Char('EMI No', size=64)
    bank_id = fields.Many2one('res.bank','Bank Details')
    emi_lines =  fields.One2many('bank.emi.lines','emi_line', 'EMI Payment Details')
    emi_start_date = fields.Date('Start Date')
    last_paid_date = fields.Date('Last Date Paid')
    next_payment_date = fields.Date('Next Payment Date')
    total_due = fields.Float('Total Due', Default=0.0)
    total_paid = fields.Float('Total Paid', Default=0.0)
    balance_due = fields.Float('Balance', Default=0.0)    
    ############ insurance Details
    ins_no = fields.Char('EMI No', size=64)
    agent_id = fields.Many2one('res.partner','Agent Details')
    ins_lines = fields.One2many('agent.ins.lines','ins_line', 'Insurance Payment Details')
    last_paid_date_ins = fields.Date('Last Date Paid')
    next_payment_date_ins = fields.Date('Next Payment Date')  
    puc_lines = fields.One2many('puc.lines','puc_line', 'PUC Details')
    vehilce_old_odometer = fields.Float('Vehicle Old Old OdoMeter', readonly=False)     
    mileage = fields.Float('Mileage', readonly=False, compute="_compute_mileage")
    fuel_odometer = fields.Float('Fuel Odometer',  default=0.0)
    related_account = fields.Many2one('account.account', required=False)
    asset_account_id = fields.Many2one('account.account','Asset Account')
    trip_commission = fields.Float('Trip Commission %')
    state = fields.Selection([('park','Parking'),('travel','Travelling'),
                                  ('maintenance','For Maintenance')], 'State', select=True)
    meter_lines = fields.One2many('vehicle.meter', 'vehicle_id', 'Meter Statement')
    fuel_lines = fields.One2many('vehicle.fuel.voucher', 'vehicle_id', 'Fuel Voucher')
    odometer = fields.Float(compute='get_odometer', string='Last Odometer', help='Odometer measure of the vehicle at this moment')
    rate_per_km = fields.Float('Rate Per Km')
    vehicle_under  =fields.Many2one('res.partner','Vehicle Under')
    per_day_rent = fields.Float('Rent Per Day')
    rent_vehicle = fields.Boolean(default=False)
    machinery = fields.Boolean(default=False)
    mach_rent_type = fields.Selection([('hours','For Hours'),
                                        ('days','For Days'),
                                        ('months','For Months')
                                        ], string="Rent Type", default="hours")
    counter_basic = fields.Float('base', digits=(20,3))
    brand_id = fields.Many2one('fleet.vehicle.model.brand', 'Brand')
    hr_driver_id = fields.Many2one('hr.employee', string='Driver', domain=[('driver_ok','=',True)])
    vehicle_ok = fields.Boolean('Vehicle')
    model_id = fields.Many2one('fleet.vehicle.model', 'Model', required=False)

    name = fields.Char(compute="_get_tms_vehicle_name", string='Nom', store=True)
    full_supply = fields.Boolean(default=False,string="Full Supply")
    full_supply_line = fields.One2many('fullsupply.line','line_id')
    capacity = fields.Float('Capacity')
    # vehicle_type = fields.Selection([('eicher','Eicher'),
    #                                 ('taurus','Taurus'),
    #                                 ('pickup','Pick Up')
    #                                 ])

    vehicle_categ_id = fields.Many2one('vehicle.category.type', string="Vehicle Type")
    eicher_categ = fields.Boolean('Eicher', compute="_compute_veh_category", store=True)
    taurus_categ = fields.Boolean('Taurus', compute="_compute_veh_category",  store=True)
    accessories = fields.Boolean(string="Accessories",default=False)
    contract_pop_up = fields.Boolean(string="Contract Popup")
    
    ############################# Vehicle status ###################################

    # from_date_status = fields.Date('From Date') 
    # to_date_status = fields.Date('To Date')






    @api.multi
    @api.depends('vehicle_categ_id')
    def _compute_veh_category(self):
        for record in self:
   #         print 'record.vehicle_categ_id------------------', record.vehicle_categ_id, self.env.ref('hiworth_tms.vehicle_category_eicher1').id
            if record.vehicle_categ_id.id == self.env.ref('hiworth_tms.vehicle_category_eicher1').id:
                record.eicher_categ = True
            elif record.vehicle_categ_id.id == self.env.ref('hiworth_tms.vehicle_category_taurus').id:
                record.taurus_categ = True
            else:
                pass


    @api.onchange('vehicle_under','full_supply')
    def onchange_full_supply_details(self):
        result = []
        if self.full_supply == True and self.vehicle_under:
            record = self.env['fleet.vehicle'].search([('vehicle_under','=', self.vehicle_under.id),('full_supply','=',True)], limit=1)
            
            for rec in record.full_supply_line:
                result.append((0, 0, {'date_from': rec.date_from, 'date_to': rec.date_to,'location_id': rec.location_id.id, 'product_id': rec.product_id.id, 'rate':rec.rate}))
            
            self.full_supply_line = result


    @api.depends('license_plate')
    def _get_tms_vehicle_name(self):
        for record in self:
            print 'vvvvvvvvvvvvvvvvvvv', record.license_plate, record.name
            record.name = record.license_plate
            print 'vvvvvvvvvvvvvvvvvvv', record.license_plate, record.name




    _defaults = {
         'state': 'park'
         }

    @api.constrains('name')
    def _check_duplicate_name(self):
        names = self.search([])
        for c in names:
            if self.id != c.id:
                if self.name and c.name:
                    if self.name.lower() == c.name.lower() or self.name.lower().replace(" ", "") == c.name.lower().replace(" ", ""):
                        raise osv.except_osv(_('Error!'), _('Error: vehicle name must be unique'))
            else:
                pass
    
    @api.model
    def create(self, vals):
        result = super(fleet_vehicle, self).create(vals)
        if result.rent_vehicle == False and result.accessories == False:
            if result.rate_per_km == 0.0:
                raise except_orm(_('Warning'),
                             _('The Rate Per Km not be zero'))
        return result


    def return_action_to_open(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        if context is None:
            context = {}
        if context.get('xml_id'):
            if context.get('tms'):
                res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid ,'tms', context['xml_id'], context=context)
            else :
                res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid ,'fleet', context['xml_id'], context=context)
            res['context'] = context
            res['context'].update({'default_vehicle_id': ids[0]})
            if context.get('tms'):
                res['context'].update({'default_state':'info','default_type':'internal'})
            res['domain'] = [('vehicle_id','=', ids[0])]
            return res
        return False


# <<<<<<< HEAD
    # @api.multi
    # def write(self, vals):
    #     result = super(fleet_vehicle, self).write(vals)
    #     if self.rent_vehicle == True:
    #         if vals.get('vehicle_under') != self.vehicle_under.id:
    #             if vals.get('vehicle_under') != self.vehicle_under.id:
    #                 raise except_orm(_('Warning'),
    #                          _('You cannot edit the vehicle owner..!!'))
# =======
    @api.multi
    def write(self, vals):
        result = super(fleet_vehicle, self).write(vals)
        if self.rent_vehicle == True:
            if vals.get('vehicle_under'):
                raise except_orm(_('Warning'),
                         _('You cannot edit the vehicle owner..!!'))
# >>>>>>> c987d8b138782ee76facfce09f088e8a88fe41b4

        return result

    
    
    @api.multi
    @api.depends('meter_lines','fuel_lines','brand_id')
    def _compute_mileage(self):
        for record in self:
            km = 0
            fuel = 0
            # for meter in record.meter_lines:
            if record.meter_lines:
                km = record.meter_lines[-1].end_value
                print 'km------------------------', km

            for rec in record.fuel_lines:
                fuel += rec.litre * rec.per_litre
            print 'fuel------------------------', fuel
            if fuel != 0:
                record.mileage = km/fuel


class VehicleCategoryType(models.Model):
    _name = 'vehicle.category.type'

    name = fields.Char(string="Vehicle Type")
    
class FullSupplyLine(models.Model):
    _name = 'fullsupply.line'

    line_id = fields.Many2one('fleet.vehicle')
    date_from = fields.Date('From')
    date_to = fields.Date('To')
    location_id = fields.Many2one('stock.location','Location')
    product_id = fields.Many2one('product.product','Product')
    rate = fields.Float('Rate')


class fleet_vehicle_cost(models.Model):
    _inherit = 'fleet.vehicle.cost'
    

    particular = fields.Char('Particular', size=64)
    qty = fields.Float('Qty')
    rate = fields.Float('Rate')



class VehicleMeter(models.Model):
    _name = 'vehicle.meter'
    _order = 'date desc'


    name = fields.Char('Name')
    date = fields.Date('Date')
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')
    start_value = fields.Float('Start Value')
    end_value = fields.Float('End Value')
    fuel_value = fields.Float('Total Fuel Refilled')


class VehicleFuelVoucher(models.Model):
    _name = 'vehicle.fuel.voucher'
    _order = 'date desc'

    @api.multi
    @api.depends('litre','per_litre')
    def compute_amount(self):
        for rec in self:
            rec.amount = rec.litre * rec.per_litre

    name = fields.Char('Name')
    date = fields.Date('Date')
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')
    pump_id = fields.Many2one('account.account', 'Pump')
    litre = fields.Float('Fuel Qty')
    per_litre = fields.Float('Fuel Price')
    amount = fields.Float(compute='compute_amount', store=True, string='Amount')
    odometer = fields.Float('Total Meter')
        
    
    
    