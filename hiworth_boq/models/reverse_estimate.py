from openerp import fields, models, api
from openerp.exceptions import Warning as UserError

class ReverseEstimate(models.Model):
	_name = 'reverse.estimate'
	_rec_name = "tender_inviting_authority"

	tender_inviting_authority = fields.Char(string="Tender Inviting Authority")
	name_of_work = fields.Many2one('project.project',string="Name of Work")
	contract_no = fields.Char(string="Contract No")
	bidder_name = fields.Many2one('res.partner',domain="[('contractor', '=', True)]", string="Bidder Name")
	re_line_ids = fields.One2many('reverse.estimate.line','re_line_id')


class ReverseEstimateLine(models.Model):
	_name = 'reverse.estimate.line'
		
	re_line_id = fields.Many2one('reverse.estimate')
	product_id = fields.Many2one('product.product',string="Item Description")
	quantity = fields.Float(string="Quantity")
	uom_id = fields.Many2one('product.uom',string="Units")
	estimated_rate = fields.Float(string="Estimated Rate")
	re_ids = fields.One2many('product.re.line','re_id')	

class ProductReLine(models.Model):
	_name = 'product.re.line'

	re_id = fields.Many2one('reverse.estimate.line')
	l = fields.Float(string="L")
	b = fields.Float(string="B")	
	d = fields.Float(string="D")
	qty = fields.Float(string="Quantity")


	