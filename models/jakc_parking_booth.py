import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError, Warning

_logger = logging.getLogger(__name__)


AVAILABLE_STATES = [    
    ('open','Open'),    
    ('reopen','Re-Open'),
    ('done','Closed'),
]

AVAILABLE_PRINTER_STATES = [
    ('enable', 'Enable'),
    ('disable', 'Disable'),
]

AVAILABLE_CAMERA_STATES = [
    ('enable', 'Enable'),
    ('disable', 'Disable'),
]

AVAILABLE_BOOTH_TYPES = [
    ('in','Booth In'),
    ('out','Booth Out'),
    ('inout','Booth In and Out'),
]

AVAILABLE_CAMERA_TYPES = [
    ('local','Local Camera'),
    ('network','Network Camera'),    
]

AVAILABLE_PRINTER_TYPES = [
    ('local','Local Printer'),
    ('network','Network Printer'),    
]

AVAILABLE_CAMERA_POSITIONS = [
    ('vehicle', 'Vehicle Camera'),
    ('driver', 'Driver Camera')
]


class ParkingBooth(models.Model):
    _name = "parking.booth"

    def trans_close(self):
        values = {}
        values.update({'state':'done'})
        self.write(values)

    def trans_re_open(self):
        values = {}
        values.update({'state':'open'})
        super(ParkingBooth,self).write(values)

    def close(self):
        values = {}
        values.update({'state': 'done'})
        self.write(values)

    def generate_sequence_number(self):
        booth = self
        sequence_number = booth.sequence_number
        values = {}
        values.update({'sequence_number': sequence_number + 1})
        super(ParkingBooth, self).write(values)
        return str(sequence_number).zfill(booth.sequence_length)

    name = fields.Char('Name', size=50, required=True)
    color = fields.Integer(string='Color Index')
    code = fields.Char('Code', size=4, required=True)
    booth_type = fields.Selection(AVAILABLE_BOOTH_TYPES, 'Type', size=16, required=True)
    
    #Valet
    is_driver = fields.Boolean('Driver Required')
    
    #Future Usage
    is_barcode = fields.Boolean('Barcode Required')
    
    #Wallet or Member
    is_card = fields.Boolean('Card Required')

    #Manless
    is_manless = fields.Boolean('Is Manless')
    manless_port = fields.Char('Manless Port', size=50, _default='/dev/ttyUSB0')
    manless_user_id = fields.Many2one('res.users', 'Manless User')
    
    #Printer
    printer_state = fields.Selection(AVAILABLE_PRINTER_STATES, 'Printer Status', size=16, default='disable')
    printer_type = fields.Selection(AVAILABLE_PRINTER_TYPES, 'Printer Type', size=16, default='local')
    printer_port = fields.Char('Printer Port', size=50, default='/dev/ttyS0')
    printer_ip = fields.Char('Printer Ip Address', size=50)
    printer_ip_port = fields.Char('Printer Ip Port', size=50)

    booth_pricing_ids = fields.One2many('parking.booth.pricing', 'booth_id', 'Pricings')
    booth_camera_ids = fields.One2many('parking.booth.camera', 'booth_id', 'Cameras')
    booth_payment_method_ids = fields.One2many('parking.booth.payment.method', 'booth_id', 'Payment Methods')
    
    #Manage Booth Sequence
    with_sequence = fields.Boolean('Sequence Enable')
    sequence_number = fields.Integer('Sequence #', default=0)
    sequence_length = fields.Integer('Sequence Length', default=5)
    
    state = fields.Selection(AVAILABLE_STATES, 'Status', size=16, default='open', readonly=True)

    def write(self, values):
        if self.state == 'done':
            raise ValidationError('Transaction Already Closed!')
        return super(ParkingBooth, self).write(values)


class ParkingBoothPricing(models.Model):
    _name = "parking.booth.pricing"

    def trans_set_default(self):
        values = {}
        values.update({'is_default': True})
        return self.write(values)
        
    def _get_default_booth_pricing(self):
        args = [('is_default','=',True)]
        ids = self.search(args)
        if ids:
            booth_pricing = self.ids[0]
            return booth_pricing
        else:
            return False

    def _enable_default_booth_pricing(self):
        values = {}
        values.update({'is_default': True})
        self.write(values)

    def _disable_default_booth_pricing(self):
        values = {}
        values.update({'is_default': False})
        self.write(values)

    booth_id = fields.Many2one('parking.booth', 'Booth', required=True)
    pricing_id = fields.Many2one('parking.pricing', 'Pricing', required=True)
    is_default = fields.Boolean('Is Default', _default=False)

    def create(self, values):
        # if 'is_default' in values.keys():
        #     if values.get('is_default'):
        #         old_default = self._get_default_booth_pricing()
        #         if old_default:
        #             self._disable_default_booth_pricing(old_default.id)
                                                
        return super(ParkingBoothPricing, self).create(values)
                    
    def write(self, values):
        # if 'is_default' in values.keys():
        #     if values.get('is_default'):
        #         old_default = self._get_default_booth_pricing()
        #         if old_default:
        #             self._disable_default_booth_pricing(old_default.id)
        
        return super(ParkingBoothPricing, self).write(values)


class ParkingBoothCamera(models.Model):
    _name = "parking.booth.camera"

    booth_id = fields.Many2one('parking.booth', 'Booth', required=True)
    camera_type = fields.Selection(AVAILABLE_CAMERA_TYPES, 'Camera Type', size=16, default='local', required=True)
    camera_state = fields.Selection(AVAILABLE_CAMERA_STATES, 'Camera Status', size=16, default='disable')
    camera_position = fields.Selection(AVAILABLE_CAMERA_POSITIONS, 'Camera Position', size=20, required=True)
    camera_device = fields.Char('Camera Device', size=50, default='/dev/video0')
    camera_ip_address = fields.Char('Camera Ip Address', size=50)
    camera_ip_port = fields.Char('Camera Ip Port', size=10)
    #state = fields.Selection(AVAILABLE_CAMERA_STATES, 'Status', size=16, default='draft')


class ParkingBoothPaymentMethod(models.Model):
    _name = "parking.booth.payment.method"

    booth_id = fields.Many2one('parking.booth', 'Booth')
    payment_method_id = fields.Many2one('parking.payment.method', 'Payment Method', required=True)
