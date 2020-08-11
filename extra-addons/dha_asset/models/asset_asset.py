# -*- coding: utf-8 -*-
import datetime
from datetime import timedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AsAssetType(models.Model):
    _name = 'as.asset.type'
    _description = 'Asset Type'

    name = fields.Char('Asset Type', required=True)
    description = fields.Char('Description',required=True)


class AsAssetGroup(models.Model):
    _name = 'as.asset.group'
    _description = 'Asset Group'

    name = fields.Char('Asset Group', required=True)
    description = fields.Char('Description',required=True)


class AsSparePart(models.Model):
    _name = 'as.sparepart'
    _description = 'Spare Part'

    name = fields.Char('Spare Part')
    product_id = fields.Many2one('product.product', string='Product')
    product_code = fields.Char('Internal Reference', related='product_id.default_code')
    quantity = fields.Integer('Quantity')
    asset_id = fields.Many2one('as.asset', string='Asset')


class AsAsset(models.Model):
    _name = 'as.asset'
    _description = 'Asset'
    _parent_store = True
    _parent_name = "parent_id"  # optional if field is 'parent_id'

    name = fields.Char('Asset', required=True)
    description = fields.Char('Description',required=True)
    type_id = fields.Many2one('as.asset.type', 'Asset Type')
    status = fields.Selection(
        [('broken', 'Broken'),
         ('decommissioned', 'Decommissioned'),
         ('inactive', 'Inactive'),
         ('missing', 'Missing'),
         ('sealed', 'Sealed'),
         ('active', 'Active'),
         ('operating', 'Operating'),
         ('limited_use', 'Limited Use'),
         ('not_ready', 'Not Ready')],
          string ='Asset Status',
          default='active'
    )
    group_id = fields.Many2one('as.asset.group', 'Asset Group')
    operator_id = fields.Many2one('hr.employee', 'Operator')
    registration = fields.Char('Registration')
    file_ids = fields.Many2many('ir.attachment', string='Attachment', ondelete='cascade')
    cover = fields.Binary('Photo')
    company_id = fields.Many2one('res.company')
    parent_id = fields.Many2one(
        'as.asset',
        string='Parent',
        ondelete='restrict',
        index=True)
    child_ids = fields.One2many(
        'as.asset', 'parent_id',
        string='Child')
    parent_path = fields.Char(index=True)
    # Meter Page
    meter_group_id = fields.Many2one('as.meter.group', string='Meter Group')
    meter_usage_ids = fields.One2many('as.meter.usage', 'asset_id', string='Meter Usage')
    # Spare Part
    spare_part_ids = fields.One2many('as.sparepart', 'asset_id', string='Spare Part')
    # Form Header
    meter_history_count =  fields.Integer(compute='compute_meter_history')
    fuel_history_count = fields.Integer(compute='compute_fuel_history')
    expense_history_count = fields.Integer(compute='compute_expense_history')
    asset_children_count = fields.Integer(compute='compute_asset_children')


    def compute_meter_history(self):
        self.ensure_one()
        self.meter_history_count = len(self.env['as.meter.his'].search([('asset_id', '=', self.id)]))

    def compute_fuel_history(self):
        self.ensure_one()
        self.fuel_history_count = len(self.env['as.fuel.his'].search([('asset_id', '=', self.id)]))

    def compute_expense_history(self):
        self.ensure_one()
        self.expense_history_count = len(self.env['as.expense.his'].search([('asset_id', '=', self.id)]))

    def compute_asset_children(self):
        self.ensure_one()
        self.asset_children_count = len(self.search([('parent_id', '=', self.id)]))

    def open_meter_history(self):
        return {
            'name': ('Meter History'),
            'domain': [('asset_id', '=', self.id)],
            'res_model': 'as.meter.his',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
        }

    def open_fuel_history(self):
        return {
            'name': ('Fuel History'),
            'domain': [('asset_id', '=', self.id)],
            'res_model': 'as.fuel.his',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
        }

    def open_expense_history(self):
        return {
            'name': ('Expense History'),
            'domain': [('asset_id', '=', self.id)],
            'res_model': 'as.expense.his',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
        }

    def open_asset_children(self):
        return {
            'name': ('Asset Children'),
            'domain': [('parent_id', '=', self.id)],
            'res_model': 'as.asset',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
        }

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError('Error! You cannot create recursive categories.')

    def action_meter_reading(self):
        self.ensure_one()
        if self.meter_usage_ids:
            wizard_id = self.env['as.enter.meter.wizard'].create({})
            [wizard_id.meter_usage_ids.create({'meter_usage_id': r.id,
                                               'fields_meter': r.meter_id.name,
                                               'fields_fuel': r.is_fuel,
                                               'fields_reading_time': datetime.datetime.today().now(),
                                               'fields_inspector_id': self.operator_id.id or False,
                                               'wizard_id': wizard_id.id})
            for r in self.meter_usage_ids]
            return {
                'name': ('Meter Reading'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'as.enter.meter.wizard',
                'view_id': self.env.ref('dha_asset.enter_meter_wizard_form').id,
                'type': 'ir.actions.act_window',
                'res_id': wizard_id.id,
                'target': 'new',
                'context': {
                    'asset_id': self.id,
                },}

    def action_expense_entry(self):
        self.ensure_one()
        wizard = self.env['as.enter.expense.wizard'].create({'asset_id': self.id,
                                                             'expense_time': datetime.datetime.today().now(),
                                                             'inspector_id': self.operator_id.id or False})
        return {
            'name': ('Expense Entry'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'as.enter.expense.wizard',
            'view_id': self.env.ref('dha_asset.enter_expense_wizard_form').id,
            'type': 'ir.actions.act_window',
            'res_id': wizard.id,
            'target': 'new',
            'context': {
                'asset_id': self.id,
            }, }





