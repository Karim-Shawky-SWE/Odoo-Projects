from odoo import fields, models

class EstatePropertyImage(models.Model):
    _name = 'estate.property.image'

    name = fields.Char(string="Name")
    property_id = fields.Many2one('estate.property', string="Property", ondelete='cascade')
    image = fields.Image(string="Image")
    sequence = fields.Integer(string="Sequence")
    description = fields.Text(string="Description")

