from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_gym_member = fields.Boolean(string='Gym Member')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('is_gym_member') and not vals.get('barcode'):
                vals['barcode'] = self.env['ir.sequence'].next_by_code('gym.member.barcode')
        return super().create(vals_list)

    @api.constrains('barcode')
    def _check_barcode_unique(self):
        for rec in self.filtered('barcode'):
            if self.search_count([('barcode', '=', rec.barcode), ('id', '!=', rec.id)]):
                raise ValidationError("This barcode is already used.")

    def action_generate_barcode(self):
        for rec in self.filtered(lambda r: not r.barcode):
            rec.barcode = self.env['ir.sequence'].next_by_code('gym.member.barcode')