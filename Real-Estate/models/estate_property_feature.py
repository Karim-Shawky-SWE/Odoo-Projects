from odoo import fields, models

class EstatePropertyFeature(models.Model):
    _name = 'estate.property.feature'

    name = fields.Char(string="Property Name", required=True)
    description = fields.Text(string="Description")
    active = fields.Boolean(default=True)