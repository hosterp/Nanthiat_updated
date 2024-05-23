from openerp import fields, models, api, _
# from openerp.osv import osv, expression
# from openerp.exceptions import Warning as UserError


class SiteExpenses(models.Model):
	_name = 'site.expenses'

	allotment_type = fields.Many2one('allotment.type', string="Allotment Type")
 	project_id = fields.Char(string="Project")
 	indus_id = fields.Char(string="Indus ID")
 	site_name = fields.Char(string="Site Name")
 	subcontractor_bill_amt = fields.Float("Sub-Contractor Bill Amount")
 	matha_transport = fields.Char("Matha Transportation")
 	sky_engineering = fields.Char("Sky Engineering")
 	vehicle_rent = fields.Float("Vehicle Rent")
 	electrical_materials = fields.Char("Electrical Materials")
 	admin_expenses = fields.Float("Admin Expenses")
 	site_statements_others = fields.Float("Site Statement & Other Expenses")
 	total_site_expenses = fields.Float("Total Site Expenses")