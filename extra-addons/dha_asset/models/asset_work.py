# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AsWorkType(models.Model):
    _name = 'as.work.type'
    _description = 'Work Type'

    name = fields.Char('Work Type', required=True)
    description = fields.Char('Description',required=True)


class AsPlanMaterial(models.Model):
    _name = 'as.plan.material'
    _description = 'Work Plan Material'

    name = fields.Char('Work Plan Material')
    product_id = fields.Many2one('product.product', string='Product')
    # ware_house_id = fields.Many2one('stock.warehouse', string='Warehouse', related='product_id.warehouse_id')
    quantity = fields.Integer('Quantity')
    unit_cost = fields.Float(string='Unit Cost', related='product_id.standard_price')
    line_cost = fields.Float(string='Line Cost', compute='compute_line_cost')
    work_order_id = fields.Many2one('as.work.order', string='Work Order')

    @api.depends('quantity', 'unit_cost')
    def compute_line_cost(self):
        for record in self:
            record.line_cost = record.quantity * record.unit_cost

class StockMove(models.Model):
    _inherit = 'stock.move'

    work_order_id = fields.Many2one('as.work.order', string='Work Order')


class AsWorkOrder(models.Model):
    _name = 'as.work.order'
    _description = 'as.work.order'


    name = fields.Char('Work Order')
    description = fields.Char('Description')

    plan_material_ids = fields.One2many('as.plan.material', 'work_order_id')
    stock_move_ids = fields.One2many('stock.move', 'work_order_id')










