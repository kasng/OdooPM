# -*- coding: utf-8 -*-
from odoo import models, fields


class AsEnterMeterWizardDetails(models.TransientModel):
    _name = 'as.enter.meter.wizard.details'

    meter_usage_id = fields.Many2one('as.meter.usage', 'Meter Usage')
    fields_meter = fields.Char(string='Meter', readonly='True')
    fields_reading = fields.Char(string='Reading')
    fields_reading_time = fields.Datetime(string='Reading Time')
    fields_inspector_id = fields.Many2one('hr.employee', 'Inspector')
    fields_fuel = fields.Boolean(string='Fuel', readonly='True')
    fields_fuel_entry = fields.Float(string='Fuel Entry')
    fields_fuel_amount = fields.Float('Fuel Amount')
    wizard_id = fields.Many2one('as.enter.meter.wizard', 'Reference')


class AsEnterMeterWizard(models.TransientModel):
    _name = 'as.enter.meter.wizard'

    meter_usage_ids = fields.One2many('as.enter.meter.wizard.details', 'wizard_id')

    def save_meter_reading(self):
        self.ensure_one()

        meter_obj = self.env['as.meter.his']
        fuel_obj = self.env['as.fuel.his']
        expense_obj = self.env['as.expense.his']

        for r in self.meter_usage_ids:
            if r.fields_reading:
                # <Meter History>
                meter_source = 'inspection'
                if r.fields_fuel_entry:
                    meter_source = 'fuel'
                meter_obj.create({
                    'asset_id': self._context.get('asset_id', False),
                    'meter_usage_id': (r.meter_usage_id.id or False),
                    'meter_reading': r.fields_reading,
                    'reading_time': r.fields_reading_time,
                    'inspector_id': (r.fields_inspector_id.id or False),
                    'meter_source': meter_source
                })
                # <Fuel History>
                if r.fields_fuel_entry:
                    fuel_obj.create({
                        'asset_id': self._context.get('asset_id', False),
                        'meter_usage_id': (r.meter_usage_id.id or False),
                        'meter_reading': r.fields_reading,
                        'reading_time': r.fields_reading_time,
                        'fuel_entry': r.fields_fuel_entry,
                        'fuel_amount': r.fields_fuel_amount,
                        'inspector_id': (r.fields_inspector_id.id or False)
                    })
                # <Expense History>
                if r.fields_fuel_amount:
                    expense_obj.create({
                        'asset_id': self._context.get('asset_id', False),
                        'meter_usage_id': (r.meter_usage_id.id or False),
                        'expense_type': 'fuel',
                        'expense_entry': r.fields_fuel_amount,
                        'expense_time': r.fields_reading_time,
                        'inspector_id': (r.fields_inspector_id.id or False)
                    })
                # <Update Last Reading>
                r.meter_usage_id.write({'last_reading': r.fields_reading})
                r.meter_usage_id.write({'last_reading_time': r.fields_reading_time})
        return True



