from openerp import fields, models, api, _
import datetime
# from openerp.osv import osv, expression
# from openerp.exceptions import Warning as UserError


class AllotmentType(models.Model):
    _name = 'allotment.type'

    name = fields.Char(string="Allotment Type")


class MasterData(models.Model):
    _name = 'master.data'
    _rec_name = 'project_id'


    @api.one
    @api.depends('work_allotted_date','work_started_date')
    def _compute_aging_to_start(self):
        d1 = ''
        d2 = ''
        d3 = datetime.datetime.strptime(fields.Date.today(), '%Y-%m-%d')
        if self.work_allotted_date:
            d1 = datetime.datetime.strptime(self.work_allotted_date, '%Y-%m-%d')
        if self.work_started_date and self.work_allotted_date:
            d2 = datetime.datetime.strptime(self.work_started_date, '%Y-%m-%d')
            self.aging_to_start = str((d2-d1).days)
        if self.work_allotted_date:
            self.aging_to_start = str((d3-d1).days)

    @api.one
    @api.depends('work_allotted_date','work_completion_date')
    def _compute_aging_to_completion(self):
        d1 = ''
        d2 = ''
        d3 = ''
        if self.work_allotted_date:
            d1 = datetime.datetime.strptime(self.work_allotted_date, '%Y-%m-%d')
        d3 = datetime.datetime.strptime(fields.Date.today(), '%Y-%m-%d')
        if self.work_completion_date and self.work_allotted_date:
            d2 = datetime.datetime.strptime(self.work_completion_date, '%Y-%m-%d')
            self.aging_to_completion = str((d2-d1).days)
        if self.work_allotted_date:        
            self.aging_to_completion = str((d3-d1).days)

    # def _compute_electrical_po(self):
    #     electrical = 0.0
    #     bill = self.env['telecom.billing'].search([('project_id','=',self.id)])       
    #     for val in bill:
    #         electrical += val.inv_amt_electrical
       
    #     self.electrical_po = electrical
        
    # def _compute_civil_po(self):
    #     civil = 0.0
    #     bill = self.env['telecom.billing'].search([('project_id','=',self.id)])       
    #     for val in bill:
    #         civil += val.inv_amt_civil
       
    #     self.civil_po = civil

    allotment_type = fields.Many2one('allotment.type', string="Allotment Type")
    project_id = fields.Char(string="Project ID")
    indus_id = fields.Char(string="Indus ID")
    site_name = fields.Char(string="Site Name")
    electrical_po = fields.Char(string="Electrical PO")
    civil_po = fields.Char(string="Civil PO")
    fse = fields.Char(string="FSE")
    site_tech_name = fields.Char(string="Site Tech Name")
    contract_number = fields.Char(string="Contact Number")
    lat = fields.Char(string="Lat")
    log = fields.Char(string="Log")
    work_type = fields.Char(string="Work Type")
    requested_opco = fields.Char(string="Requested Opco")
    anchor_opco = fields.Char(string="Anchor OPCO")
    district = fields.Char(string="District")
    work_allotted_date = fields.Date(string="Work Allotted Date", default=fields.Date.today())
    site_supervisor = fields.Many2one('hr.employee', string="Site Supervisor")
    sub_contractor = fields.Char(string="Sub-Contractor")  
    work_started_date = fields.Date(string="Work Started Date")
    aging_to_start = fields.Integer(string="Aging(Allotment to Start)", compute='_compute_aging_to_start')
    work_status_electrical = fields.Char(string="Electrical Work Status")
    work_status_civil = fields.Char(string="Civil/Pole Work Status")
    overall_status = fields.Char(string="Over all Status")
    work_completion_date = fields.Date(string="Work Completion Date")
    m_sheet_status = fields.Char(string="M Sheet Status")
    aging_to_completion = fields.Integer(string="Aging(Allotment to Completion)", compute='_compute_aging_to_completion')
    pr_value_electrical = fields.Float(string="PR Value(Electrical Work)")
    pr_value_civil = fields.Float(string="PR Value(Civil/Pole Work)")
    qty_amendment_electrical = fields.Char(string="Qty Amendment(Elec. PO)")
    qty_amendment_civil = fields.Char(string="Qty Amendment(Civil/Pole PO)")
    line_addition_electrical = fields.Char(string="Line Addition(Elec. PO)")
    line_addition_civil = fields.Char(string="Line Addition(Civil/Pole PO)")
    wcc_status_electrical = fields.Char(string="Electrical PO WCC Status")
    wcc_status_civil = fields.Float(string="Civil/Pole PO WCC Status")
    invoice_status_electrical = fields.Float(string="Invoice Status of Electrical PO")
    invoice_status_civil = fields.Float(string="Invoice Status of Civil/Pole PO")
    inv_amt_electrical = fields.Char(string="Electrical Invoice Amount")
    inv_amt_civil = fields.Char(string="Civil Invoice Amount")
    payment_sts_electrical = fields.Char(string="Payment Status of Electrical PO")
    payment_sts_civil = fields.Char(string="Payment Status of Civil/Pole PO")
    total_received_amt = fields.Float(string="Total Received Amount")
    dg = fields.Char(string="DG")
    stabilizer = fields.Char(string="Stabilizer")
    sps_amf_piu_sp = fields.Char(string="SPS/AMF/PIU/SP")
    battery_bank = fields.Char(string="Battery Bank")
    bb_cabinet = fields.Char(string="BB Cabinet")
    smps = fields.Char(string="SMPS")
    modules = fields.Char(string="Modules")
    aircon = fields.Char(string="Aircon")
    dc_converter = fields.Char(string="DC DC Converter")
    txn_rack = fields.Char(string="TXN Rack")
    dcem = fields.Char(string="DCEM")
    od_plinth = fields.Char(string="OD Plinth")
    contact_number = fields.Char(string="Contact Number")

    subcontractor_bill_amt = fields.Float("Sub-Contractor Bill Amount")
    matha_transport = fields.Float("Matha Transportation")
    sky_engineering = fields.Float("Sky Engineering")
    vehicle_rent = fields.Float("Vehicle Rent")    
    electrical_materials = fields.Float("Electrical Materials")
    admin_expenses = fields.Float("Admin Expenses")
    site_statements_others = fields.Float("Site Statement & Other Expenses")
    total_site_expenses = fields.Float("Total Site Expenses")

    state = fields.Selection([
                            ('draft','Draft'),
                            ('ongoing','Ongoing'),
                            ('close','Closed'),
                            ], string='Status', readonly=True, default='draft')


    @api.multi
    def button_ongoing(self):
        self.work_started_date = fields.Date.today()
        self.state = 'ongoing'


    @api.multi
    def button_close(self):
        self.work_completion_date = fields.Date.today()
        self.state = 'close'



   