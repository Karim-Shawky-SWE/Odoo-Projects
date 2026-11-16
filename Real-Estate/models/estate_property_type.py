from odoo import api, fields, models

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'

    name = fields.Char(string="Type", required=True)
    description = fields.Text(string="Description")

    active = fields.Boolean(default=True)

