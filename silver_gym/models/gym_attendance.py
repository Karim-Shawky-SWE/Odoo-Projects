from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError

class GymAttendance(models.Model):
    _name = 'gym.attendance.created'
    _description = 'Gym Attendance'

    partner_id = fields.Many2one('res.partner', string='Client')
    subscription_id = fields.Many2one('subscription', string='Subscription')
    check_in = fields.Datetime(string='Check In', default=fields.Datetime.now, readonly=True)

    session_type = fields.Selection(string='Session Type', selection=[
        ('gym', 'Gym'),
        ('private', 'Private Session'),
        ('spa', 'Spa Session')
    ], default='gym')

