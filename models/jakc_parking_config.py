import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning

_logger = logging.getLogger(__name__)

class parking_config(models.Model):
    _name = 'parking.config'
    _description = 'Parking Management Config'
    
    def get_config(self, cr, uid, context=None):
        ids = self.search(cr, uid, [('state','=', True),], context=context)
        if ids:
            return self.browse(cr, uid, ids[0], context=context)
        else:
            return None
            
    _columns = {
        'erp_server': fields.char('ERP Server', size=50),        
        'report_server': fields.char('Report Server', size=50),
        'report_server_port': fields.char('Report Server Port', size=50),
        'report_user': fields.char('Report User', size=50),
        'report_password': fields.char('Report Password', size=50),
        'state': fields.boolean('Status'),
    }
    
    _defaults = {
        'erp_server': lambda *a:'localhost',         
        'state': lambda *a: True,
    }
    
parking_config()

class parking_config_settings(osv.osv_memory):
    _name = 'parking.config.settings'
    _inherit = 'res.config.settings'
    _columns = {
        'erp_server': fields.char('ERP Server', size=50),
        'report_server': fields.char('Report Server', size=50),
        'report_server_port': fields.char('Report Server Port', size=50),
        'report_user': fields.char('Report User', size=50),
        'report_password': fields.char('Report Password', size=50),        
    }

    def _get_config(self, cr, uid, context=None):
        ids = self.pool.get('parking.config').search(cr, uid, [('state','=', True),], context=context)
        if ids:
            config  = self.pool.get('parking.config').browse(cr, uid, ids[0], context=context)
        else:
            config = None
        return config

    def get_default_erp_server(self, cr, uid, fields, context=None):
        config = self._get_config(cr, uid, context)
        if config:
            erp_server = config.erp_server 
        else: 
            data = {}
            result_id = self.pool.get('parking.config').create(cr, uid, data, context=context)
            erp_server = None
        return {'erp_server': erp_server}


    def set_default_erp_server(self, cr, uid, ids, context=None):
        config = self._get_config(cr, uid, context)
        setting = self.browse(cr, uid, ids[0], context)
        erp_server = setting.erp_server
        self.pool.get('parking.config').write(cr, uid, [config.id], {'erp_server': erp_server})
    
    def get_default_report_server(self, cr, uid, fields, context=None):
        config = self._get_config(cr, uid, context)
        if config:
            report_server = config.report_server
        else: 
            data = {}
            result_id = self.pool.get('parking.config').create(cr, uid, data, context=context)
            report_server = None
        return {'report_server': report_server}

    def set_default_report_server(self, cr, uid, ids, context=None):
        config = self._get_config(cr, uid, context)
        setting = self.browse(cr, uid, ids[0], context)
        report_server = setting.report_server
        self.pool.get('parking.config').write(cr, uid, [config.id], {'report_server': report_server})


    def get_default_report_server_port(self, cr, uid, fields, context=None):
        config = self._get_config(cr, uid, context)
        if config:
            report_server_port = config.report_server_port
        else: 
            data = {}
            result_id = self.pool.get('parking.config').create(cr, uid, data, context=context)
            report_server_port = None
        return {'report_server_port': report_server_port}

    def set_default_report_server_port(self, cr, uid, ids, context=None):
        config = self._get_config(cr, uid, context)
        setting = self.browse(cr, uid, ids[0], context)
        report_server_port = setting.report_server_port
        self.pool.get('parking.config').write(cr, uid, [config.id], {'report_server_port': report_server_port})

        
    def get_default_report_user(self, cr, uid, fields, context=None):
        config = self._get_config(cr, uid, context)
        if config:
            report_user = config.report_user
        else: 
            data = {}
            result_id = self.pool.get('parking.config').create(cr, uid, data, context=context)
            report_user = None
        return {'report_user': report_user}

    def set_default_report_user(self, cr, uid, ids, context=None):
        config = self._get_config(cr, uid, context)
        setting = self.browse(cr, uid, ids[0], context)
        report_user = setting.report_user
        self.pool.get('parking.config').write(cr, uid, [config.id], {'report_user': report_user})
    
    def get_default_report_password(self, cr, uid, fields, context=None):
        config = self._get_config(cr, uid, context)
        if config:
            report_password = config.report_password
        else: 
            data = {}
            result_id = self.pool.get('parking.config').create(cr, uid, data, context=context)
            report_password = None
        return {'report_password': report_password}

    def set_default_report_password(self, cr, uid, ids, context=None):
        config = self._get_config(cr, uid, context)
        setting = self.browse(cr, uid, ids[0], context)
        report_password = setting.report_password
        self.pool.get('parking.config').write(cr, uid, [config.id], {'report_password': report_password})    
         