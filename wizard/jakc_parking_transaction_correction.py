from odoo import models, fields, api, _abcoll
from odoo.exceptions import ValidationError, UserError, Warning


class WizardParkingTransactionCorrection(models.TransientModel):
    _name = 'wizard.parking.transaction.correction'

    correction_type = fields.Selection([('manual_out', 'Manual Out'),
                                        ('cancel','Cancel')], 'Correction Type', required=True)

    