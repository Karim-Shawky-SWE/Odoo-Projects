from odoo import fields, models, api

class EstateProperty(models.Model):
    _name = 'estate.property'

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")
    property_type_id = fields.Many2one('estate.property.type')
    owner_id = fields.Many2one('res.partner', string="Owner")
    salesperson_id = fields.Many2one('res.users', string='Salesperson')
    company_id = fields.Many2one('res.company', string='Company')
    postcode = fields.Char(string="Postcode")
    address = fields.Char(string="Address")
    bedrooms = fields.Integer(string="Bedrooms", required=True)
    bathrooms = fields.Integer(string="Bathrooms")
    living_area = fields.Float(string="Living Area (M²)")
    is_garden = fields.Boolean(default=False)
    garden_area = fields.Integer(string="Garden Area (M²)", required=True)
    expected_price = fields.Monetary(string="Expected Price")
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id", string="Currency", readonly=True)
    is_available = fields.Boolean(default=True)
    status = fields.Selection([
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('sold', 'Sold'),
        ('rented', 'Rented'),
    ], default='available')
    date_listed = fields.Date(string="Date Listed", default= fields.Date.today())

    feature_ids = fields.Many2many('estate.property.feature', string='Features')
    images_ids = fields.One2many('estate.property.image', string='Images')
    total_area = fields.Float(string="Total Area", compute='_compute_total_area')
    owner_phone = fields.Char(related='owner_id.phone', string="Owner Phone")
    property_type_name = fields.Char(related='property_type_id.name', string="Property Type Name")


    @api.depends('garden_area', 'living_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.garden_area + record.living_area
            