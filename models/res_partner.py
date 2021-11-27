import logging
from datetime import datetime, date
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning
from operator import itemgetter

_logger = logging.getLogger(__name__)


AVAILABLE_STATES = [    
    ('draft','New'),                
    ('open','Open'),    
    ('done','Closed'),
    ('posted','Posted'),
    ('cancel', 'Cancelled'),
]


AVAILABLE_MEMBER_STATE = [
    ('draft', 'New'),
    ('none', 'Non Member'),
    ('canceled', 'Cancelled Member'),
    ('old', 'Old Member'),
    ('expired', 'Expired'),
    ('waiting', 'Waiting Member'),
    ('invoiced', 'Invoiced Member'),
    ('free', 'Free Member'),
    ('paid', 'Paid Member'),
    ('done', 'Close'),
]


class ResPartner(models.Model):
    _inherit = "res.partner"

    def get_car_count(self):
        for partner in self:
            count = 0
            for membership in partner.parking_membership_ids:
                if membership.state == 'open':
                    count += 1
        self.car_count = count

    is_parking_member = fields.Boolean('Is Parking Member')
    is_employee = fields.Boolean('Is Employee')
    parking_membership_ids = fields.One2many('parking.membership', 'res_partner_id', 'Parking Membership')
    car_count = fields.Integer(compute="get_car_count", string='Car #')


class ParkingMembership(models.Model):
    _name = "parking.membership"
    _inherit = ['mail.thread']
    _rec_name = 'plat_number'

    def trans_confirm(self):
        self.write({'state': 'open'})

    def trans_re_open(self):
        values = {}
        values.update({'state':'open'})
        self.write(values)

    def generate_membership_id(self):
        _logger.info('Start Generate Membership ID')        
        trans_seq_id = self.env['ir.sequence'].get('parking.membership.sequence')
        trans_data = {}
        trans_data.update({'membership_id':trans_seq_id[0]})        
        super(ParkingMembership,self).write(trans_data)
        _logger.info('End Generate Membership ID')

    def _is_car_in_parking_area(self):
        _logger.info('Start Is Car In Parking Area')
        _logger.info('End Is Car In Parking Area')
        
    def _get_last_membership(self):
        _logger.info('Start Get Last Membership')

        _logger.info('End Get Last Membership')

    def check_valid_payment(self):
        status = False
        tzinfo = timezone('Asia/Jakarta')
        str_now = date.today()
        _logger.debug("Now : " + str_now.strftime('%Y-%m-%d %H:%M:%S'))
        membership_payment_ids = self.membership_payment_ids
        for line in membership_payment_ids:
            if line.state == 'paid':
                _logger.debug(line)
                start_date = line.start_date
                end_date = line.end_date
                if start_date < str_now and end_date > str_now:
                    status = True
                    break
        return status

    def get_expired_date(self):
        for row in self:
            if len(row.membership_payment_ids) > 0:
                payments = row.mapped('membership_payment_ids').filtered(lambda o : o.payment_state == 'paid').sorted('end_date',reverse=True)
                if len(payments) > 0:
                    row.expire_date = payments[0].end_date
                else:
                    row.expire_date = False

    def print_receipt(self):
        pass

    
    membership_id = fields.Char('Membership #', size=10, readonly=True)
    res_partner_id = fields.Many2one('res.partner', 'Customer', required=True)
    plat_number = fields.Char('Plat Number', size=10, required=True)
    card_number = fields.Char('Card Number', size=20)
    product_id = fields.Many2one('product.product', 'Product')
    expire_date = fields.Date('Expired Date', compute='get_expired_date', readonly=True)
    membership_payment_ids = fields.One2many('parking.membership.payment', 'parking_membership_id', 'Payments')
    state = fields.Selection(AVAILABLE_MEMBER_STATE, 'Status', readonly=True, default='draft')

    @api.model
    def create(self, values):
        result = super(ParkingMembership,self).create(values)
        result.generate_membership_id()
        return result

    _sql_constraints = [
        ('member_unit', 'UNIQUE (membership_id, plat_number)',  'You can not have two plat number with the same customer !')
    ]

class ParkingMembershipPayment(models.Model):
    _name = "parking.membership.payment"
    _rec_name = 'parking_membership_id'

    def _prepare_invoice_values(self):
        invoice_vals = {
            'ref': self.parking_membership_id.plat_number,
            'move_type': 'out_invoice',
            'invoice_origin': f'Payment for {self.parking_membership_id.plat_number} ({self.start_date} - {self.end_date})',
            'invoice_user_id': self.env.user.id,
            'partner_id': self.parking_membership_id.res_partner_id.id
        }

        return invoice_vals

    def trans_create_invoice(self):
        invoice_vals = self._prepare_invoice_values()
        invoice_id = self.env['account.move'].sudo().create(invoice_vals).with_user(self.env.uid)

        # partner_id = self.parking_membership_id.res_partner_id
        # invoice = self.env['account.invoice'].create({
        #     'partner_id': partner_id.id,
        #     'account_id': partner_id.property_account_receivable_id.id,
        #     'fiscal_position_id': partner_id.property_account_position_id.id,
        #     'comment': 'Payment Non Billing for ' + self.start_date.strftime('%d/%m/%Y') + ' to ' + self.end_date.strftime('%d/%m/%Y')
        # })
        # line_values = {
        #     'product_id': self.parking_membership_id.product_id.id,
        #     'price_unit': self.total_amount,
        #     'invoice_id': invoice.id,
        # }
        # # create a record in cache, apply onchange then revert back to a dictionnary
        # invoice_line = self.env['account.invoice.line'].new(line_values)
        # invoice_line._onchange_product_id()
        # line_values = invoice_line._convert_to_write({name: invoice_line[name] for name in invoice_line._cache})
        # line_values['price_unit'] = self.total_amount
        # invoice.write({'invoice_line_ids': [(0, 0, line_values)]})
        # invoice.compute_taxes()
        self.invoice_id = invoice_id.id

    @api.onchange('payment_duration', 'start_date')
    def onchange_payment_duration(self):
        if self.parking_membership_id and self.start_date and self.payment_duration > 0:
            self.end_date = self.start_date + relativedelta(months=self.payment_duration)
            self.total_amount = self.parking_membership_id.product_id.list_price * self.payment_duration

    def get_state(self):
        for row in self:
            str_now = date.today()
            if row.end_date > str_now:
                if row.invoice_id:
                    row.state = row.invoice_id.state
                else:
                    row.state = 'draft'
            else:
                row.state = 'done'


    parking_membership_id = fields.Many2one('parking.membership', 'Parking Membership', required=True)
    trans_date = fields.Date('Transaction Date', readonly=True, default=date.today())
    payment_duration = fields.Integer('Payment Duration (in month)', required=True, default=1)
    billing_type = fields.Selection([('nobilling','Non Billing'),('billing','Billing')],'Billing Type', default='nobilling', required=True)
    start_date = fields.Date('Start Date', required=True, default=date.today())
    end_date = fields.Date('End Date', readonly=True, default=date.today() + relativedelta(months=1))
    total_amount = fields.Float('Total Payment', readonly=True)
    invoice_id = fields.Many2one('account.move', 'Invoice', readonly=True)
    payment_state = fields.Selection(selection=[
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('reversed', 'Reversed'),
        ('invoicing_legacy', 'Invoicing App Legacy')],
        string="Payment Status", related='invoice_id.payment_state')

    state = fields.Selection(AVAILABLE_STATES, 'State', compute='get_state', readonly=True)


    @api.model
    def create(self, values):
        parking_membership_obj = self.env['parking.membership']
        parking_membership = parking_membership_obj.browse(values.get('parking_membership_id'))
        end_date = datetime.today() + relativedelta(months=values.get('payment_duration'))
        values.update({'end_date': end_date})
        values.update({'total_amount' : parking_membership.product_id.list_price * values.get('payment_duration')})
        return super(ParkingMembershipPayment, self).create(values)

    def write(self, values):
        trans = self
        if trans.state == 'paid':
            raise ValidationError('Transaction Already Paid!')
        
        if 'state' in values.keys():
            if values.get('state') == 'invoiced':
                return self._create_invoice(values)

        if 'payment_duration' in values.keys():
            #end_date = datetime.strptime(self.start_date,'%Y-%m-%d') + relativedelta(months=values.get('payment_duration'))
            end_date = self.start_date + relativedelta(months=values.get('payment_duration'))
            values.update({'end_date': end_date})
            values.update({'total_amount': trans.parking_membership_id.product_id.list_price * values.get('payment_duration')})
        return super(ParkingMembershipPayment, self).write(values)

