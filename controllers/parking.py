import re
import ast
import functools
import logging
import json
from datetime import datetime, date
import werkzeug.wrappers
from odoo.exceptions import ValidationError, AccessError
from odoo.addons.weha_smart_parking.common import invalid_response, valid_response

from odoo import http
from odoo.http import request

from odoo.addons.weha_smart_parking.common import (
    extract_arguments,
    invalid_response,
    valid_response,
)


_logger = logging.getLogger(__name__)

def validate_token(func):
    """."""

    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        access_token = request.httprequest.headers.get("access_token")
        if not access_token:
            return invalid_response("access_token_not_found", "missing access token in request header", 401)
        access_token_data = (
            request.env["api.access_token"].sudo().search([("token", "=", access_token)], order="id DESC", limit=1)
        )

        if access_token_data.find_one_or_create_token(user_id=access_token_data.user_id.id) != access_token:
            #data = json.loads(request.httprequest.data) 
            #_logger.info(request.httprequest.environ)
            if request.httprequest.environ['CONTENT_TYPE'] == 'application/json':
                return {"err": True,"message": "Token Invalid", "data":[]}
            else:
                return invalid_response("access_token", "token seems to have expired or invalid", 401)
           

        request.session.uid = access_token_data.user_id.id
        request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)

    return wrap

class ParkingController(http.Controller):
    
    @validate_token
    @http.route("/api/v1/parking/checkmember/<member_id>", type="http", auth="none", methods=["GET"], csrf=False)
    def parking_checkmember(self, member_id):
        response_data = {
            "err": False,
            "message": "Success",
            "data": []
        }
        return valid_response(response_data)

    @validate_token
    @http.route("/api/v1/parking/booth-code/<code>", type="http", auth="none", methods=["GET"], csrf=False)
    def parking_checkmember(self, code):
        booth_id = http.request.env['parking.booth'].search([('code','=',code)], limit=1)
        if not booth_id:
            data = {
                "err": True,
                "message": "Booth not found",
                "data": [ 
                ]
            }
            return valid_response(data)
        raw_data = booth_id.read()
        response_data = {
            "err": False,
            "message": "Success",
            "data": raw_data
        }
        return valid_response(response_data)

    @validate_token
    @http.route("/api/v1/parking/session", type="http", auth="none", methods=["POST"], csrf=False)
    def parking_session(self, **post):
        booth_id = int(post['booth_id']) or False if 'booth_id' in post else False
        operator_id = int(post['operator_id']) or False if 'operator_id' in post else False

        vals = {
            'booth_id': booth_id,
            'operator_id': operator_id,
        }

        parking_session_id = http.request.env['parking.transaction.session'].create(vals)
        
        if not parking_session_id:
            data = {
                "err": True,
                "message": "Error Create Parking Session",
                "data": [ 
                ]
            }
            return valid_response(data)
        
        response_data = {
            "err": False,
            "message": "Success",
            "data": {
                'id': parking_session_id.id,
                'name': parking_session_id.name,
                'shift_id': parking_session_id.shift_id.id
            }
        }
        return valid_response(response_data)

    @validate_token
    @http.route("/api/v1/parking/entry", type="http", auth="none", methods=["POST"], csrf=False)
    def parking_entry(self, **post):
        
        entry_booth_id = int(post['entry_booth_id']) or False if 'entry_booth_id' in post else False
        input_method =  post['input_method'] or False if 'input_method' in post else False #
        entry_operator_id = int(post['entry_operator_id']) or False if 'entry_operator_id' in post else False
        is_member = int(post['is_member']) or False if 'is_member' in post else False
        _logger.info(type(is_member))
        if is_member == 0:
            _fields_includes_in_body = all([entry_booth_id,input_method])
            barcode = False
        else:
            barcode = post['barcode'] or False if 'barcode' in post else False
            _fields_includes_in_body = all([entry_booth_id,input_method,barcode])

        if not _fields_includes_in_body:
            data =  {
                "err": True,
                "message": "Missing fields",
                "data": []
            }
            return valid_response(data)
        
        if is_member == 0:
            vals = {
                'entry_booth_id': entry_booth_id,
                'input_method': input_method,
                'entry_operator_id': entry_operator_id,
            } 
        else:
            vals = {
                'entry_booth_id': entry_booth_id,
                'barcode': barcode,
                'input_method': input_method,
                'entry_operator_id': entry_operator_id,
            }

        try:
            parking_transaction_id = http.request.env['parking.transaction'].create(vals)
            if parking_transaction_id:
                data = {
                    "err": False,
                    "message": "",
                    "data": [ 
                        {
                            'name': parking_transaction_id.barcode,
                            'entry_datetime': parking_transaction_id.entry_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                            'entry_booth_id': parking_transaction_id.entry_booth_id.name,
                            'entry_operator_id': parking_transaction_id.entry_operator_id.name
                        }
                    ]
                }
                return valid_response(data)
            else:
                data = {
                    "err": True,
                    "message": "Error Create Parking Transaction",
                    "data": [ 
                    ]
                }
                return valid_response(data)
        except Exception as e:
            data = {
                "err": True,
                "message": str(e),
                "data": [ 
                    {'message': 'Error Create Parking Transaction'}
                ]
            }
            return valid_response(data)

    @validate_token
    @http.route("/api/v1/parking/pre-exit", type="http", auth="none", methods=["POST"], csrf=False)
    def parking_pre_exit(self, **post):
        trans_id = post['trans_id'] or False if 'trans_id' in post else False
        plat_number = post['plat_number'] or False if 'plat_number' in post else False
        parking_session_id = int(post['parking_session_id']) or False if 'parking_session_id' in post else False
        exit_booth_id = int(post['exit_booth_id']) or False if 'exit_booth_id' in post else False
        exit_operator_id = int(post['exit_operator_id']) or False if 'exit_operator_id' in post else False
        
        _logger.info(parking_session_id)
        _fields_includes_in_body = all([trans_id,plat_number,parking_session_id,exit_booth_id,exit_operator_id])

        if not _fields_includes_in_body:
            data =  {
                "err": True,
                "message": "Missing fields",
                "data": []
            }
            return valid_response(data)
        
        domain  = [
            ('trans_id','=', trans_id),
            ('state','=', 'entry')
        ]
        
        parking_transaction_id = http.request.env['parking.transaction'].search(domain, limit=1)
        _logger.info(parking_transaction_id)
        if not parking_transaction_id:
            data = {
                "err": True,
                "message": "Parking Transaction not found",
                "data": [ 
                ]
            }
            return valid_response(data)
        
        vals = {
            'plat_number': plat_number,
            'exit_booth_id': exit_booth_id,
            'exit_operator_id': exit_operator_id,
            'session_id': parking_session_id,
        }

        try:
            parking_transaction_id.prepare_exit_operator_transaction(vals)
        except ValidationError as err:
            data = {
                "err": True,
                "message": "Error Prepare Exit Transaction",
                "data": [ 
                ]
            }
            return valid_response(data)
        
        data = {
            "err": False,
            "message": "Transaction Found",
            "data": {
                'id': parking_transaction_id.id, 
                'trans_id': parking_transaction_id.trans_id,
                'barcode': parking_transaction_id.barcode,
                'plat_number': parking_transaction_id.plat_number,
                'input_method': parking_transaction_id.input_method,
                'entry_datetime': parking_transaction_id.entry_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                'exit_datetime': parking_transaction_id.exit_datetime.strftime('%Y-%m-%d %H:%M:%S')
            },
        }
        return valid_response(data)

    @validate_token
    @http.route("/api/v1/parking/post-exit", type="http", auth="none", methods=["POST"], csrf=False)
    def parking_post_exit(self, **post):
        parking_transaction_id = int(post['parking_transaction_id']) or False if 'parking_transaction_id' in post else False
        pricing_id = int(post['pricing_id']) or False if 'pricing_id' in post else False
        parking_transaction_id = http.request.env['parking.transaction'].browse(parking_transaction_id)
        if not parking_transaction_id:
            data = {
                "err": True,
                "message": "Parking Transaction not found",
                "data": [ 
                ]
            }
            return valid_response(data)

        if parking_transaction_id.state != 'exit':
            data = {
                "err": True,
                "message": "Parking Transaction invalid",
                "data": [ 
                ]
            }
            return valid_response(data)

        #Set Pricing ID
        parking_transaction_id.pricing_id = pricing_id

        try:
            parking_transaction_id.calculate_duration()
        except Exception as e:
            data = {
                "err": True,
                "message": str(e),
                "data": [ 
                    {'message': 'Error Calculate Duration'}
                ]
            }
            return valid_response(data)

        try:
            parking_transaction_id.calculate_general_charge()
        except Exception as e:
            data = {
                "err": True,
                "message": str(e),
                "data": [ 
                    {'message': 'Error Calculate General Charge'}
                ]
            }
            return valid_response(data)

        try:
            parking_transaction_id.calculate_service_charge()
        except Exception as e:
            data = {
                "err": True,
                "message": str(e),
                "data": [ 
                    {'message': 'Error Calculate Service Charge'}
                ]
            }
            return valid_response(data)

        try:
            if parking_transaction_id.is_pinalty:
                parking_transaction_id.calculate_missing_charge()
        except Exception as e:
            data = {
                "err": True,
                "message": str(e),
                "data": [ 
                    {'message': 'Error Calculate Missing Charge'}
                ]
            }
            return valid_response(data)
        try:
            parking_transaction_id.calculate_total_amount()
        except Exception as e:
            data = {
                "err": True,
                "message": str(e),
                "data": [ 
                    {'message': 'Error Calculate Total Amount'}
                ]
            }
            return valid_response(data)

        try:
            parking_transaction_id.trans_close()
        except Exception as e:
            data = {
                "err": True,
                "message": str(e),
                "data": [ 
                    {'message': 'Error Close Parking Transaction'}
                ]
            }
            return valid_response(data)


        data = {
            "err": False,
            "message": "Transaction Success",
            "data": {
                'id': parking_transaction_id.id, 
            },
        }
        return valid_response(data)

    @validate_token
    @http.route("/api/v1/parking/checkbarcode/<barcode>", type="http", auth="none", methods=["GET"], csrf=False)
    def parking_check_barcode(self, barcode):
        domain  = [
            ('barcode','=', barcode),
            ('state','=', 'entry')
        ]
        parking_transaction_id = http.request.env['parking.transaction'].search(domain)
        _logger.info(parking_transaction_id)
        if not parking_transaction_id:
            data = {
                "err": True,
                "message": "Parking Transaction not found",
                "data": [ 
                ]
            }
            return valid_response(data)

       
        data = {
            "err": False,
            "message": "Transaction Found",
            "data": {
                'id': parking_transaction_id.id, 
                'trans_id': parking_transaction_id.trans_id,
                'barcode': parking_transaction_id.barcode,
                'plat_number': parking_transaction_id.plat_number,
                'input_method': parking_transaction_id.input_method,
                'entry_datetime': parking_transaction_id.entry_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            },
        }
        return valid_response(data)
        
    @validate_token
    @http.route("/api/v1/parking/pinalty", type="http", auth="none", methods=["POST"], csrf=False)
    def parking_pinalty(self, **post):
        pass