import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.osv import fields, osv

_logger = logging.getLogger(__name__)

class parking_membership_payment_invoice(osv.osv_memory):
    _name = "parking.membership.payment.invoice"
    _description = "Parking Membership Payment Invoice"
    
    def onchange_payment_duration(self, cr, uid, ids, payment_duration=False):        
        if not payment_duration:
            return {'value': {'end_date': False}}
        end_date = datetime.today()+ relativedelta(months=payment_duration)        
        return {'value': {'end_date': end_date.strftime('%Y-%m-%d')}}
    
    
    _columns = {
        'parking_membership_id': fields.many2one('parking.membership','Parking Membership', required=True, readonly=True),
        'trans_date': fields.date('Transaction Date', required=True, readonly=True),
        'payment_duration': fields.integer('Payment Duration (in month)'),
        'start_date': fields.date('Start Date', readonly=True),
        'end_date': fields.date('End Date', readonly=True),                                
    }
    
    _defaults = {
        'parking_membership_id': lambda self, cr, uid, context: context.get('parking_membership_id', False),
        'trans_date': fields.date.context_today,     
        'payment_duration': lambda *a: 1,
    }    
        
parking_membership_payment_invoice()
    