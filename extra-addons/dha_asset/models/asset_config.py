# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AsUnit(models.Model):
    _name = 'as.unit'
    _description = 'Unit of Measure'

    name = fields.Char('Unit', required=True)
    description = fields.Char('Description',required=True)


class AsFuelType(models.Model):
    _name = 'as.fuel.type'
    _description = 'Fuel Type'

    name = fields.Char('Fuel Type', required=True)
    description = fields.Char('Description',required=True)


class AsMeter(models.Model):
    _name = 'as.meter'
    _description = 'Meter'

    name = fields.Char('Meter', required=True)
    description = fields.Char('Description',required=True)
    meter_type = fields.Selection(
        [('continiuos', 'Continiuos'),
         ('gauge', 'Gauge'),
         ('characteristic', 'Characteristic')],
         string='Meter Type',
         default='continiuos')
    reading_type = fields.Selection(
        [('actual', 'Actual'),
         ('delta', 'Delta')],
         string='Reading Type',
         default='actual')
    unit_id = fields.Many2one('as.unit', string='Unit of Measure')



class AsMeterGroup(models.Model):
    _name = 'as.meter.group'
    _description = 'Meter Group'

    name = fields.Char('Meter Group', required=True)
    description = fields.Char('Description',required=True)
    meter_ids = fields.Many2many('as.meter', string='Meter')


class AsMeterUsage(models.Model):
    _name = 'as.meter.usage'
    _description = 'Meter Usage'

    name = fields.Char('Meter Usage')
    meter_id = fields.Many2one('as.meter', string='Meter', required=True)
    description = fields.Char('Description', related='meter_id.description', readonly=True)
    meter_type = fields.Selection(string='Meter Type', related='meter_id.meter_type', readonly=True)
    reading_type = fields.Selection(string='Reading Type', related='meter_id.reading_type', readonly=True)
    unit_id = fields.Many2one(string='Unit',related='meter_id.unit_id', readonly=True)
    last_reading = fields.Char('Last Reading', required=True)
    last_reading_time = fields.Datetime('Last Reading Time', required=True)
    is_fuel = fields.Boolean('Fuel')
    fuel_type_id = fields.Many2one('as.fuel.type', string='Fuel Type')
    asset_id = fields.Many2one('as.asset', string='Asset')


class AsSpecAttribute(models.Model):
    _name = 'as.spec.attribute'
    _description = 'Attribute'

    name = fields.Char('Attribute', required=True)
    description = fields.Char('Description',required=True)
    unit_id = fields.Many2one('as.unit', string='Unit of Measure')


class AsSpecClass(models.Model):
    _name = 'as.spec.class'
    _description = 'Classification'

    name = fields.Char('Classification', required=True)
    description = fields.Char('Description',required=True)
    attribute_ids = fields.Many2many('as.spec.attribute', string='Attribute')

