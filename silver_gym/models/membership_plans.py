from odoo import api, fields, models
from odoo.exceptions import ValidationError

class MembershipPlans(models.Model):
    _name = 'membership.plan'
    _description = 'Membership'

    membership_plan_type = fields.Selection([
        ('normal', 'Normal'),
        ('private', 'Private'),
        ('bundle', 'Bundle'),
    ], default='normal', required=True)

    # General info
    name = fields.Char(string='Name')
    duration = fields.Integer(string='Duration (Month)')
    private_sessions = fields.Integer(string='private sessions')
    price = fields.Float(string='Price')
    notes = fields.Char(string='Notes')

    # Regular Membership
    inbody = fields.Integer(string='inbody')
    spa_sessions = fields.Integer(string='spa')
    freeze_days = fields.Integer(string='freeze days')

    @api.constrains('freeze_days')
    def _compute_freeze_days(self):
        for plan in self:
            if plan.freeze_days < 0:
                raise ValidationError('Validation error message')
