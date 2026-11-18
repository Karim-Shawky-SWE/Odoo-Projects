from odoo import fields, models, api
from datetime import timedelta

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'

    name = fields.Char(string="Offer Reference", readonly=True, copy=False, default='New')
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)
    price = fields.Monetary(string="Price", required=True)
    currency_id = fields.Many2one('res.currency', required=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
    ])
    validity = fields.Integer(string="Validity (Days)", default=7)
    date_deadline = fields.Date(string="Date of Deadline", compute="_compute_date_deadline", store=True, readonly=True)

    @api.depends('validity', 'create_date')
    def _compute_date_deadline(self):
        for record in self:
            start = record.create_date or fields.Datetime.now()
            record.date_deadline = (start + timedelta(days=record.validity)).date()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('estate.property.offer') or 'New'
        return super().create(vals_list)
