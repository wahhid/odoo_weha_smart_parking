import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError, Warning

_logger = logging.getLogger(__name__)


AVAILABLE_STATES = [    
    ('open','Open'),    
    ('done','Closed'),
]


class ParkingPricing(models.Model):
    _name = "parking.pricing"

    name = fields.Char('Name', size=50, required=True)
    image1 = fields.Binary('Image')
    code = fields.Char('Code', size=1, required=True)
    vehicle_type_id = fields.Many2one('parking.vehicle.type', 'Vechile Type', required=True)
    init_duration = fields.Integer('Initial Duration', required=True, default=0)
    first_hour_charge = fields.Float('First Hour', required=True, default=0)
    second_hour_charge = fields.Float('Second Hour', required=True, default=0)
    third_hour_charge = fields.Float('Third Hour', required=True, default=0)
    next_hour_charge = fields.Float('Next Hour', required=True, default=0)
    service_charge = fields.Float('Service', required=True, default=0)
    pinalty_charge = fields.Float('Pinalty', required=True, default=0)
    state = fields.Selection(AVAILABLE_STATES, 'Status', size=16, readonly=True, default='open')

    _sql_constraints = [
        ('uniq_name', 'unique(name)', "Pricing already exists with this name . pricing name must be unique!"),
    ]