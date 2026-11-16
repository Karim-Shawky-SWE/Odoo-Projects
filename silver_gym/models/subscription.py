from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

import logging
import requests
from datetime import datetime, time, timedelta

_logger = logging.getLogger(__name__)
GRAPH_URL = "https://graph.facebook.com/v21.0/%s/messages"


class Subscription(models.Model):
    _name = 'subscription'
    _description = 'subscription'

    is_confirmed = fields.Boolean(string='Confirmed', default=False, copy=False)

    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True, copy=False)
    payment_state =fields.Selection(related='invoice_id.payment_state', string='Payment State', copy=False)

    partner_id = fields.Many2one('res.partner', string='Client')
    membership_plan_id = fields.Many2one('membership.plan', required=True,domain="[('membership_plan_type', '!=', 'private')]")
    private_plan_id = fields.Many2one('membership.plan', string='Private Plan',domain="[('membership_plan_type', '=', 'private')]")
    start_date = fields.Datetime(string='Start Date', default=fields.Datetime.now)
    end_date = fields.Datetime(string='End Date', compute='_compute_end_date', store=True)
    quantity = fields.Integer(string='Quantity', default=1, copy=False)

    price = fields.Float(string='Price', related='membership_plan_id.price')
    duration = fields.Integer(string='Duration (Month)', related='membership_plan_id.duration')
    spa_session = fields.Integer(related='membership_plan_id.spa_sessions', string='Number of Spa Sessions')
    notes = fields.Char(string='Notes', related='membership_plan_id.notes')

    private_session = fields.Integer(related = 'membership_plan_id.private_sessions',string='Plan Private Sessions')
    private_plan_sessions = fields.Integer(related='private_plan_id.private_sessions')
    private_plan_price = fields.Float(related='private_plan_id.price', string='Private Price')
    used_private_sessions = fields.Integer()
    total_private_sessions = fields.Integer(compute='_compute_total_private_sessions', string='Total Private Sessions', default=0, readonly=True)

    is_freeze = fields.Boolean(string='Freeze', readonly=True, copy=False)
    freeze_days = fields.Integer(string='Freezable Days', related='membership_plan_id.freeze_days')
    frozen_days = fields.Integer(string='Frozen Days', default=0, readonly=True, copy=False)
    remaining_freeze_days = fields.Integer(string='Remaining Freeze Days',
                                           compute='_compute_remaining_freeze_days', store=True)
    days_to_freeze = fields.Integer(string='Days to Freeze')
    freeze_start_date = fields.Datetime(string='Freeze Start Date', readonly=True, copy=False)
    freeze_end_date = fields.Datetime(string='Freeze End Date', readonly=True, copy=False)

    @api.depends('dependency_field')
    def _compute_computed_field(self):
        """Compute the value of the field computed_field."""
        for record in self:
            record.computed_field = 0.0  # Your computation here
    is_private = fields.Boolean(string='Private')

    total_price = fields.Float(string='Total Price', compute='_compute_total_price')

    trainer_id = fields.Many2one('hr.employee', string='Personal Trainer', domain=([('job_id.name', '=', 'Trainer')]))
    state = fields.Selection([
        ('active', 'Active'),
        ('expire_soon', 'Expire Soon'),
        ('expired', 'Expired'),
    ],default ="active",store=True)

    inbody = fields.Integer(string='Inbody', related='membership_plan_id.inbody')
    used_inbody = fields.Integer(string='Used Inbody')
    remaining_inbody = fields.Integer(string='Remaining Inbody', computed='_remaining_inbody')

    used_spa_sessions = fields.Integer(string='Used Spa Sessions', default=0, copy=False)
    remaining_spa_sessions = fields.Integer(
        string='Remaining Spa Sessions',
        compute='_compute_remaining_spa_sessions',
    )

    attendance_counter = fields.Integer(string='Attendance Counter', default = 0, copy=False, readonly=True)
    last_check_in = fields.Datetime(string='Last Check In', readonly=True, copy=False)

    reminder_sent = fields.Boolean(string='Reminder Sent', default=False, copy=False)

    @api.constrains('quantity')
    def check_quantity(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError('Quantity must be greater than 0')

    @api.constrains('used_spa_sessions')
    def _check_used_spa_sessions(self):
        for record in self:
            if not record.used_spa_sessions <= record.spa_session:
                raise UserError('Used Spa Sessions is More Than the Plan Provided Sessions')

    @api.depends('membership_plan_id', 'inbody', 'used_inbody')
    def _remaining_inbody(self):
        for record in self:
            record.remaining_inbody = record.inbody - record.used_inbody

    @api.depends('spa_session', 'used_spa_sessions')
    def _compute_remaining_spa_sessions(self):
        for record in self:
            record.remaining_spa_sessions = record.spa_session - record.used_spa_sessions

    @api.depends('freeze_days', 'frozen_days')
    def _compute_remaining_freeze_days(self):
        for record in self:
            record.remaining_freeze_days = record.freeze_days - record.frozen_days

    @api.depends('start_date', 'duration', 'frozen_days', 'membership_plan_id')
    def _compute_end_date(self):
        for record in self:
            if record.membership_plan_id and record.start_date:
                record.end_date = record.start_date + timedelta(days=record.duration * 30) + timedelta(
                    days=record.frozen_days)
            else:
                record.end_date = False

    @api.depends('membership_plan_id', 'private_plan_price','is_private', 'quantity')
    def _compute_total_price(self):
        for record in self:
            if record.is_private:
                record.total_price = record.private_plan_price + (record.price * record.quantity)
            else:
                record.total_price = (record.price * record.quantity)

    @api.depends( 'is_private', 'membership_plan_id', 'private_plan_id', 'used_private_sessions')
    def _compute_total_private_sessions(self):
        for record in self:
            if record.is_private and record.private_plan_sessions > 0:
                record.total_private_sessions = record.private_plan_sessions + record.private_session - record.used_private_sessions
            else:
                record.total_private_sessions = record.private_session - record.used_private_sessions

    @api.model
    def _cron_check_subscription_state(self, num_days=7):
        now = fields.Datetime.now()
        deadline = now + timedelta(days=num_days)
        for record in self.search([('end_date', '!=', False)]):

            if record.end_date <= now:
                new_state = 'expired'
            elif record.end_date <= deadline:
                new_state = 'expire_soon'
            else:
                new_state = 'active'
            if record.state != new_state:
                record.state = new_state

    @api.model
    def _cron_check_is_freeze(self):
        now = fields.Datetime.now()
        self.search([
            ('is_freeze', '=', True),
            ('freeze_end_date', '<=', now),
        ]).write({'is_freeze': False})

    def action_freeze(self):
        now = fields.Datetime.now()
        for record in self:
            if record.state == 'expired':
                raise ValidationError('Could not freeze an expired membership.')
            if record.is_freeze:
                raise ValidationError('This membership is already frozen.')
            if record.days_to_freeze <= 0:
                raise ValidationError('Enter the number of days to freeze.')
            if record.days_to_freeze > record.remaining_freeze_days:
                raise ValidationError('Not enough freeze days left.')
            record.write({
                'is_freeze': True,
                'freeze_start_date': now,
                'freeze_end_date': now + timedelta(days=record.days_to_freeze),
                'frozen_days': record.frozen_days + record.days_to_freeze,
                'days_to_freeze': 0,
            })
        self._cron_check_subscription_state()

    def cancel_freeze(self):
        for record in self:
            freezed_days = (fields.Datetime.now() - record.freeze_start_date).days
            expected_freeze_days = (record.freeze_end_date - record.freeze_start_date).days
            record.write({
                'is_freeze': False,
                'freeze_start_date': False,
                'freeze_end_date': False,
                'frozen_days': (record.frozen_days - expected_freeze_days) + freezed_days,
                'days_to_freeze': 0,
            })
        self._cron_check_subscription_state()

    def confirm_subscription(self):
        self.ensure_one()
        if self.invoice_id:
            raise UserError('Invoice already exists.')
        if not self.membership_plan_id:
            raise UserError('No membership plan is selected.')

        lines = [(0,0,{
            'name': self.membership_plan_id.name,
            'quantity': self.quantity,
            'price_unit': self.price,
        })]
        if self.is_private:
            lines.append((0,0,{
                'name': self.private_plan_id.name,
                'quantity': 1,
                'price_unit': self.private_plan_price,
            }))

        invoice = self.env['account.move'].create({
            'partner_id': self.partner_id.id,
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': lines,
        })

        invoice.action_post()
        self.invoice_id = invoice
        self.is_confirmed = True
        return True

    @api.model
    def _normalize_phone(self, phone):
        """Egypt: 01012345678 -> 201012345678"""
        digits = ''.join(c for c in (phone or '') if c.isdigit())
        if digits.startswith('00'):
            digits = digits[2:]
        if digits.startswith('0'):
            digits = '20' + digits[1:]
        return digits

    def _send_whatsapp_reminder(self):
        self.ensure_one()
        icp = self.env['ir.config_parameter'].sudo()
        phone_id = icp.get_param('whatsapp.phone_number_id')
        token = icp.get_param('whatsapp.access_token')
        template = icp.get_param('whatsapp.template_name')
        if not (phone_id and token and template):
            _logger.error("WhatsApp parameters are not configured")
            return False

        partner = self.partner_id
        raw_phone = partner.phone or (partner.mobile if 'mobile' in partner._fields else '')
        phone = self._normalize_phone(raw_phone)
        if not phone:
            _logger.warning("No phone number for %s", partner.display_name)
            return False

        end_local = fields.Datetime.context_timestamp(self, self.end_date)
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": template,
                "language": {"code": "en"},
                "components": [{
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": partner.name},
                        {"type": "text", "text": end_local.strftime('%d/%m/%Y')},
                    ],
                }],
            },
        }
        try:
            resp = requests.post(
                GRAPH_URL % phone_id,
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
                timeout=15,
            )
            if resp.status_code == 200:
                return True
            _logger.error("WhatsApp API error %s: %s", resp.status_code, resp.text)
        except requests.RequestException as e:
            _logger.error("WhatsApp request failed: %s", e)
        return False

    @api.model
    def _cron_send_expiry_reminders(self):
        target = fields.Date.context_today(self) + timedelta(days=7)
        day_start = datetime.combine(target, time.min)
        day_end = datetime.combine(target, time.max)
        subs = self.search([
            ('is_confirmed', '=', True),
            ('state', '!=', 'expired'),
            ('end_date', '>=', day_start),
            ('end_date', '<=', day_end),
            ('reminder_sent', '=', False),
            ('partner_id', '!=', False),
        ])
        for sub in subs:
            if sub._send_whatsapp_reminder():
                sub.reminder_sent = True
                self.env.cr.commit()