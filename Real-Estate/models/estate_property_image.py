from odoo import fields, models

class EstatePropertyImage(models.Model):
    _name = 'estate.property.image'

    name = fields.Char(string="Name", required=True)
    property_id = fields.Many2one('estate.property', string="Property", ondelete='cascade', required=True)
    image = fields.Image(string="Image", required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    description = fields.Text(string="Description")

