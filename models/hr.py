import logging

from openerp import models, fields, osv
from openerp.exceptions import ValidationError, Warning

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    is_valet_driver = fields.Boolean('Is Valet Driver')
