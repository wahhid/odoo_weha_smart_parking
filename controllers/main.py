from openerp import http

import logging

_logger = logging.getLogger(__name__)


class WebsiteParking(http.Controller):

    

    @http.route('/parking/trans/operator/index', type='http', auth='public')
    def parking_trans_operator(self, platnumber=None):
        data = {}
        return http.request.render('jakc_parking.parking_transaction_manless_index', data)

    @http.route('/parking/trans/manless/index', type='http', auth='public')
    def parking_trans_manless(self):
        data = {}
        return http.request.render('jakc_parking.parking_transaction_manless_index', data)