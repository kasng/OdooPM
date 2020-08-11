# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AsMeterHistory(models.Model):
    _name = 'as.meter.his'
    _description = 'Meter History'

    name = fields.Char('Meter History')
    asset_id = fields.Many2one('as.asset', string='Asset', readonly=True)
    asset_description = fields.Char(string='Description', related='asset_id.description')
    meter_usage_id = fields.Many2one('as.meter.usage', string='Meter Usage')
    meter_id = fields.Many2one('as.meter', string='Meter', related='meter_usage_id.meter_id')
    meter_type = fields.Selection(
        [('continiuos', 'Continiuos'),
         ('gauge', 'Gauge'),
         ('characteristic', 'Characteristic')],
        string='Meter Type', related='meter_id.meter_type')
    reading_type = fields.Selection(
        [('actual', 'Actual'),
         ('delta', 'Delta')],
        string='Reading Type', related='meter_id.reading_type')
    unit_id = fields.Many2one('as.unit', string='Unit of Measure', related='meter_id.unit_id')
    meter_reading = fields.Char('Reading')
    reading_time = fields.Datetime('Reading Time')
    inspector_id = fields.Many2one('hr.employee', string='Inspector', readonly=True)
    meter_source = fields.Selection(
        [('inspection', 'Inspection'),
         ('fuel', 'Fuel'),
         ('work_order', 'Work Order')],
        string='Meter Source', readonly=True)



class AsFuelHistory(models.Model):
    _name = 'as.fuel.his'
    _description = 'Fuel History'

    name = fields.Char('Fuel History')
    asset_id = fields.Many2one('as.asset', string='Asset', readonly=True)
    asset_description = fields.Char(string='Description', related='asset_id.description')
    meter_usage_id = fields.Many2one('as.meter.usage', string='Meter Usage')
    meter_id = fields.Many2one('as.meter', string='Meter', related='meter_usage_id.meter_id')
    meter_reading = fields.Char('Meter Reading', readonly=True)
    reading_time = fields.Datetime('Reading Time', readonly=True)
    fuel_type_id = fields.Many2one('as.fuel.type', string='Fuel Type', related='meter_usage_id.fuel_type_id')
    fuel_entry = fields.Float(string='Fuel Entry')
    fuel_amount = fields.Float(string='Amount (VND)')
    fuel_unit_price = fields.Float(string='Unit Price', compute='_compute_fuel_unit_price', store=False)
    inspector_id = fields.Many2one('hr.employee', string='Inspector', readonly=True)

    @api.depends('fuel_entry', 'fuel_amount')
    def _compute_fuel_unit_price(self):
        for record in self:
            output = 0.0
            if record.fuel_entry:
                output = record.fuel_amount / record.fuel_entry
            record.fuel_unit_price = output


class AsExpenseHistory(models.Model):
    _name = 'as.expense.his'
    _description = 'Expense History'

    name = fields.Char('Expense History')
    asset_id = fields.Many2one('as.asset', string='Asset', readonly=True)
    asset_description = fields.Char(string='Description', related='asset_id.description')
    expense_type = fields.Selection(
        [('fuel', 'Fuel Entry'),
         ('tolls', 'Tolls Entry'),
         ('service', 'Service'),
         ('work_order', 'Work Order'),
         ('registration', 'Registration'),
         ('insurance', 'Insurance'),
         ('miscellaneous', 'Miscellaneous')],
        string='Expense Type', default='fuel', readonly=True)
    expense_entry = fields.Float('Expense (VND)')
    expense_time = fields.Datetime('Expense Time')
    inspector_id = fields.Many2one('hr.employee', string='Operator', readonly=True)
    meter_usage_id = fields.Many2one('as.meter.usage', string='Meter Usage')

