from openerp import fields, models, api, _
# from openerp.osv import osv, expression
# from openerp.exceptions import Warning as UserError


class TelecomBilling(models.Model):
	_name = 'telecom.billing'

	allotment_type = fields.Many2one('allotment.type', string="Allotment Type")
	project_id = fields.Many2one('master.data', string="Project")
	indus_id = fields.Char(string="Indus ID")
	site_name = fields.Char(string="Site Name")
	m_sheet_status = fields.Char(string="M Sheet Status")
	aging = fields.Float(string="Aging(Allotment to Completion)")
	subcontractor_bill_amt = fields.Float(string="Sub-Contractor Bill Amount")
	pr_value_electrical = fields.Float(string="PR Value(Electrical Work)")
	pr_value_civil = fields.Float(string="PR Value(Civil/Pole Work)")
	qty_amendment_electrical = fields.Float(string="Qty Amendment(Elec. PO)")
	qty_amendment_civil = fields.Float(string="Qty Amendment(Civil/Pole PO)")
	line_addition_electrical = fields.Float(string="Line Addition(Elec. PO)")
	line_addition_civil = fields.Float(string="Line Addition(Civil/Pole PO)")
	wcc_status_electrical = fields.Float(string="Electrical PO WCC Status")
	wcc_status_civil = fields.Float(string="Civil/Pole PO WCC Status")
	invoice_sts_electrical = fields.Float(string="Invoice Status of Electrical PO")
	invoice_sts_civil = fields.Float(string="Invoice Status of Civil/Pole PO")
	inv_amt_electrical = fields.Float(string="Electrical Invoice Amount")
	inv_amt_civil = fields.Float(string="Civil Invoice Amount")
	payment_sts_electrical = fields.Char(string="Payment Status of Electrical PO")
	payment_sts_civil = fields.Char(string="Payment Status of Civil/Pole PO")
	total_receive_amt = fields.Float(string="Total Received Amount")
