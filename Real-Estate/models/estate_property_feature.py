from odoo import fields, models

class EstatePropertyFeature(models.Model):
    _name = 'estate.property.feature'

    name = fields.Char(string="Property Name")
    description = fields.Char(string="Description")
    active = fields.Boolean(default=True)