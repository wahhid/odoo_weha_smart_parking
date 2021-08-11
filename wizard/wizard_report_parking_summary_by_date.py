from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime
from dateutil import relativedelta

class WizardParkingSummaryByDate(models.TransientModel):
    _name = 'wizard.parking.summary.by.date'
    _description = 'Parking Summary By Date Report'

    start_date = fields.Date('Start Date', required=True, default=datetime.today())
    end_date = fields.Date('End Date', required=True, default=datetime.today())


    def generate_report(self):
        data = {'start_date': self.start_date, 'end_date': self.end_date}
        return self.env['report'].get_action([], 'jakc_parking.report_parkingsummarybydate', data=data)