from openerp import fields, models, api, _
from openerp.osv import osv, expression
from openerp.exceptions import Warning as UserError


class SiteAllocation(models.Model):
	_name = 'site.allocation'

	allotment_type = fields.Many2one('allotment.type', string="Allotment Type")
	project_id = fields.Char(string="Project")
	indus_id = fields.Char(string="Indus ID")
	site_name = fields.Char(string="Site Name")
	electrical_po = fields.Char(string="Electrical PO")
	civil_po = fields.Char(string="Civil PO")
	site_supervisor = fields.Char(string="Site Supervisor")
	sub_contractor = fields.Char(string="Sub Contractor")
	work_started_date = fields.Date(string="Work Started Date")
	aging = fields.Float(string="Aging(Allotment to Start)")
	work_status_electrical = fields.Char(string="Electrical Work Status")
	work_status_civil = fields.Char(string="Civil/Pole Work Status")
	overall_status = fields.Char(string="Overall Status")
	work_completion_date = fields.Date(string="Work Completion Date")