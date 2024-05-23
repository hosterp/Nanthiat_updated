from openerp import fields, models, api, _
# from openerp.osv import osv, expression
# from openerp.exceptions import Warning as UserError


class SiteCreation(models.Model):
	_name = 'site.creation'

	allotment_type = fields.Many2one('allotment.type', string="Allotment Type")
 	project_id = fields.Char(string="Project")
 	indus_id = fields.Char(string="Indus ID")
 	site_name = fields.Char(string="Site Name")
 	electrical_po = fields.Char(string="Electriccl PO")
 	civil_po = fields.Char(string="Civil PO")
 	fse = fields.Char(string="FSE")
 	site_tech_name = fields.Char(string="Site Tech. Name")
 	contact_number = fields.Char(string="Contact Number")
 	lat = fields.Char(string="Lat")
 	log = fields.Char(string="Log")
 	work_type = fields.Char(string="Work Type")
 	requested_opco = fields.Char(string="Requested OPCO")
 	anchor_opco = fields.Char(string="Anchor OPCO")
 	district = fields.Many2one('master.district', string="District")
 	work_alloted_date = fields.Date(string="Work Alloted Date")
 	dg = fields.Char(string="DG")
 	stabilizer = fields.Char(string="Stabilizer")
 	sps_amf_piu_sp = fields.Char(string="SPS/AMF/PIU/SP")
 	battery_bank = fields.Char(string="Battery Bank")
 	bb_cabinet = fields.Char(string="BB Cabinet")
 	smps = fields.Char(string="SMPS")
 	modules = fields.Char(string="Modules")
 	aircon = fields.Char(string="Aircon")
 	dc_converter =fields.Char(string="DC DC Converter")   
 	txn_rack = fields.Char(string="TXN Rack")
 	dcem = fields.Char(string="DCEM")
 	od_plinth = fields.Char(string="OD Plinth")
