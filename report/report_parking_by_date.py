import logging
from datetime import timedelta
from functools import partial

import psycopg2
import pytz

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class ReportParkingSummaryByDate(models.AbstractModel):

    _name = 'report.jakc_parking.report_parkingsummarybydate'

    def get_parking_summary_by_date(self, date_start, date_stop):
        """ Serialise the orders of the day information
        params: date_start, date_stop string representing the datetime of order
        """
        #Get Session Information
        self.env.cr.execute("""
                              SELECT b.session_date as session_date,
                                     b.operator_id as operator_id,
                                     d.login as login,
                                     c.name as pricing_name,  
                                     COUNT(*) as quantity,
                                     SUM(a.casual_charging) as casual_charging,
                                     SUM(a.service_charging) as service_charging,
                                     SUM(a.pinalty_charging) as pinalty_charging,
                                     SUM(a.total_amount) as total_amount
                              FROM parking_transaction a
                              LEFT JOIN parking_transaction_session b on b.id = a.session_id
                              LEFT JOIN parking_pricing c on c.id = a.pricing_id
                              LEFT JOIN res_users d ON d.id = b.operator_id
                              WHERE  b.session_date BETWEEN '{}' AND '{}' AND (a.state='exit' or a.state='done')
                              GROUP BY b.session_date, b.operator_id, d.login, c.name
                              ORDER BY b.session_date, c.name
                          """.format(date_start, date_stop))
        session_summary_ids = self.env.cr.dictfetchall()
        session_summary_lines = []
        for line in session_summary_ids:
            val = {}
            val.update({'session_date': line['session_date']})
            val.update({'login': line['login']})
            val.update({'pricing_name': line['pricing_name']})
            val.update({'quantity': line['quantity']})
            val.update({'casual_charging': line['casual_charging']})
            val.update({'service_charging': line['service_charging']})
            val.update({'pinalty_charging': line['pinalty_charging']})
            val.update({'total_amount': line['total_amount']})
            session_summary_lines.append(val)
        result = {}
        result.update({
            'session_summaries': session_summary_lines,
        })
        return result

    def render_html(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_parking_summary_by_date(data['start_date'],data['end_date']))
        return self.env['report'].render('jakc_parking.report_parkingsummarybydate', data)
