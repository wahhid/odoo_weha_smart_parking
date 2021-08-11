import logging

from openerp.osv import fields, osv

_logger = logging.getLogger(__name__)

class parking_transaction_session_correction(osv.osv_memory):
    _name = "parking.transaction.session.correction"
    _description = "Parking Transaction Session Correction"
            
    def trans_correction(self, cr, uid, ids, context=None):
        _logger.info("Start Transaction Correction")
        params = self.browse(cr, uid, ids, context=context)
        param = params[0]
        print param
        print param.parking_transaction_session_id
        print param.session_date
        session =  self.pool.get('parking.transaction.session').browse(cr, uid, param.parking_transaction_session_id, context=context)        
        values = {}
        values.update({'session_date': param.session_date})        
        _logger.info("End Transaction Correction")
        return self.pool.get('parking.transaction.session').correction(cr, uid, [session.id], values, context=context)
        
    _columns = {
        'parking_transaction_session_id': fields.many2one('parking.transaction.session','Parking Transaction Session', required=True, readonly=True),
        'session_date': fields.date('Session Date', required=True),
    }
    
    _defaults = {
        'parking_transaction_session_id': lambda self, cr, uid, context: context.get('parking_transaction_session_id', False),
        'session_date': fields.date.context_today,     
    }    
        
parking_transaction_session_correction()
    