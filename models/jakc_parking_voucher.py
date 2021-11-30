# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author:LINTO CT(<https://www.cybrosys.com>)

#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################
import string
import random
from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError, UserError


class ParkingVoucher(models.Model):
    _name = 'parking.voucher'

    def generate_voucher(self):
        pass

    name = fields.Char(string="Name", required=True)
    voucher_val = fields.Integer(string="Voucher Value", required=True)
    expiry_date = fields.Date(string="Expiry Date", required=True, help='The expiry date of Voucher.')


class ParkingVoucherLine(models.Model):
    _name = 'parking.voucher.line'

    def get_code(self):
        size = 7
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(size))

    _sql_constraints = [
        ('name_uniq', 'unique (code)', "Code already exists !"),
    ]
        
    voucher_id = fields.Many2one('parking.voucher', string="Voucher #")
    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", default=get_code)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    voucher_val = fields.Float(string="Voucher Value", help='The amount for the voucher.')
