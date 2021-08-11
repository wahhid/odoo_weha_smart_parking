from odoo import api, fields, models
from odoo.exceptions import UserError


class WizardSurveySummary(models.TransientModel):
    _name = 'wizard.parking.session.summary'
    _description = 'Parking Session Summary Report'

    user_id = fields.Many2one('res.users', 'Operator', required=True)
    session_id = fields.Many2one('parking.transaction.session', 'Session', required=True)

    def generate_report(self):
        data = {'session_id': self.session_id.id}
        return self.env['report'].get_action([], 'jakc_parking.report_parkingsessionsummary', data=data)