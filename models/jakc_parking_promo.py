from odoo.exceptions import UserError
from odoo import models, fields, _, api


class ParkingPromotion(models.Model):
    _name = 'parking.promotion'

    def _get_default_currency_id(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char(string="Name", required=True)
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    


class ParkingPromotionRule(models.Model):
    _name = 'parking.promotion.rule'

    promotion_id = fields.Many2one('parking.promotion', string="Promotion Rule")

    applied_on = fields.Selection([('vehicle_type', 'Vehicle Type')], string="Applied On", default='product', required=True)
    min_quantity = fields.Integer(string="Minimum Quantity")
    vehicle_type_ids = fields.Many2many()
    promotion_rule_lines = fields.One2many('sale.promotion.rule.line', 'promotion_rule_id', string="Promotion Lines")

    @api.constrains('date_start', 'date_end')
    def check_date(self):
        if self.date_start and self.date_end:
            if self.date_end < self.date_start:
                raise UserError(_('Please check the Ending date.'))

    @api.constrains('promotion_rule_lines')
    def check_promotion(self):
        if not self.promotion_rule_lines:
            raise UserError(_('Please Add some promotion products.'))


class SalePromotionLines(models.Model):
    _name = 'sale.promotion.rule.line'

    product_id = fields.Many2one('product.product', string="Product")
    quantity = fields.Integer(string="Quantity")
    promotion_rule_id = fields.Many2one('sale.promotion.rule', string="Promotion Lines")