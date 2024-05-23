from openerp import fields, models, api, _
from openerp.exceptions import Warning as UserError

class MasteSubDistrict(models.Model):
	_name = 'master.sub.district'

	name = fields.Char(string="Sub District")

class MasterThaluk(models.Model):
	_name = 'master.thaluk'

	name = fields.Char(string="Thaluk")

class MasterVillage(models.Model):
	_name = 'master.village'

	name = fields.Char(string="Village")

class PreDeedDetails(models.Model):
	_name = 'pre.deed.details'

	pre_deed_id = fields.Many2one('property.details')
	pre_deed_date = fields.Date(string="Date of Pre-Deed")
	pre_title_owner = fields.Many2one('res.partner', string="Pre-Title Owner")
	pre_deed_no = fields.Char(string="Pre-Deed No")
	doc_type = fields.Char(string="Document Type")

class BankValueDetails(models.Model):
	_name = 'bank.value.details'

	bank_value_id = fields.Many2one('property.details')
	date = fields.Date(string="Bank Valuation Date")
	valuer = fields.Char(string="Bank Valuer")
	mobile = fields.Char(string="Mobile")
	bank_value = fields.Float(string="Bank Value")

class PropertyDetails(models.Model):
	_name = 'property.details'
	_rec_name = 'reg_no'

	reg_no = fields.Char(string="Document No")
	reg_date = fields.Date(string="Date of Registration") 
	thandaper = fields.Char(string="Thandaper")
	location = fields.Many2one('stock.location', string="Location", domain=[('usage','=','internal')])
	title_value = fields.Float(string="Title Value")
	stamp_value = fields.Float(string="Stamp Value")
	reg_fee = fields.Float(string="Reg. Fee") #2% on fair 
	h_ed_fee = fields.Float(string="H.Ed. Fee")
	cess = fields.Float(string="Cess")
	title_owner = fields.Many2one('res.partner', string="Title Deed Owner", domain="[('res_company_new', '=', True)]")
	survey_no = fields.Char(string="Survey No.")
	re_sy_no = fields.Char(string="Re Survey No.")
	hr = fields.Float(string="Hr")
	are = fields.Float(string="Are")
	sqm = fields.Float(string="Sqm")
	total_cents = fields.Float(string="Total Cents")
	block = fields.Many2one('master.block', string="Block")
	district = fields.Many2one('master.district', string="District")
	sub_district = fields.Many2one('master.sub.district', string="Sub District")
	thaluk = fields.Many2one('master.thaluk', string="Thaluk")
	village = fields.Many2one('master.village', string="Village")
	muri =fields.Char(string="Muri")
	panchayath = fields.Many2one('master.panchayath', string="Panchayath")
	sub_registrar_office = fields.Char(string="Sub Registrar Office (SRO)")
	pledge_bank = fields.Many2one('res.partner.bank', string="Pledge Bank")
	type_id = fields.Many2one(string="Type", related='pledge_bank.bank_acc_type_id')
	remarks = fields.Text(string="Remarks")
	tax_payment_date = fields.Date(string="Date of Tax Payment")
	state = fields.Selection([('in_hand','In Hand'),('sold','Sold Out')], default="in_hand")
	
	released_gehan = fields.Char(string="Released Gehan")
	possession = fields.Char(string="Possession Certificate")
	location_sketch = fields.Char(string="Location Sketch")

	fair_value = fields.Float(string="Fair Value")
	reg_fee = fields.Float(string="Registration Fee")
	writing = fields.Float(string="Writing Fee")
	writers_details = fields.Text(string="Writers Details")
	other_exp = fields.Float(string="Other Expenses")
	market_value = fields.Float(string="Market Value")
	hypo_bank = fields.Char(string="Hypothecation Bank")
	collateral = fields.Char(string="Collateral")
	land_type = fields.Char(string="Type of Land")
	total_extent = fields.Char(string="Total Extent")
	land_tax = fields.Many2one('account.tax',string="Land tax")
	ec = fields.Char(string="EC")

	pre_deed_ids = fields.One2many('pre.deed.details','pre_deed_id',string="Pre Deed Details")
	bank_value_ids = fields.One2many('bank.value.details','bank_value_id',string="Bank Value Details")

	@api.multi
	def action_sold(self):
		self.state = 'sold'





	