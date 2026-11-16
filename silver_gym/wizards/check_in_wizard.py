from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

class CheckInWizard(models.TransientModel):
    _name = 'check_in.wizard'
    _description = 'Check in Wizard'

    phone = fields.Char('Phone')
    barcode = fields.Char('Barcode')

    session_type = fields.Selection([
        ('gym', 'Gym'),
        ('private', 'Private Session'),
        ('spa', 'Spa Session'),
        ('inbody', 'In-Body'),
    ], string='Session Type', default='gym')

    def _search_partner(self):
        self.ensure_one()
        if self.phone:
            domain = [('phone','=',self.phone.strip())]
        elif self.barcode:
            domain = [('barcode', '=', self.barcode.strip())]
        else:
            raise UserError('Enter a phone or barcode')

        partners = self.env['res.partner'].search(domain)

        if not partners:
            raise UserError('No partner found')
        if len(partners) > 1:
            raise UserError('More than one partner found')

        return partners[0]


    def _search_subscription(self, partner):
        subscriptions = self.env['subscription'].search(
            [('partner_id', '=', partner.id), ('state', '!=', 'expired')])

        if not subscriptions:
            raise UserError('No subscription found')
        if len(subscriptions) > 1:
            raise UserError('More than one subscription found')

        return subscriptions[0]

    def check_in_confirm(self):

        partner = self._search_partner()
        subscription = self._search_subscription(partner)

        if subscription.is_freeze:
            raise UserError('Subscription is freeze')

        if not subscription.is_confirmed:
            raise UserError('Subscription is not confirmed')

        if self.session_type == 'spa':
            if subscription.spa_session <= 0:
                raise UserError('No spa sessions left')
            subscription.used_spa_sessions += 1
        elif self.session_type == 'private':
            if subscription.total_private_sessions <= 0:
                raise UserError('No private sessions left')
            subscription.used_private_sessions += 1

        subscription.attendance_counter +=1
        subscription.last_check_in = fields.Datetime.now()

        if self.session_type != 'gym':
            self.env['gym.attendance.created'].create({
                'partner_id': partner.id,
                'subscription_id': subscription.id,
                'session_type': self.session_type,
            })
