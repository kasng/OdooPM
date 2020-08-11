# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AsLocationType(models.Model):
    _name = 'as.location.type'
    _description = 'Location Type'

    name = fields.Char('Location Type', required=True)
    description = fields.Char('Description',required=True)


class AsLocation(models.Model):
    _name = 'as.location'
    _description = 'Location'
    _parent_store = True
    _parent_name = "parent_id"  # optional if field is 'parent_id'

    name = fields.Char('Location', required=True)
    description = fields.Char('Description',required=True)
    type = fields.Many2one('as.location.type', string='Type')
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
        string='Status',
        default='active'
    )
    file = fields.Many2many('ir.attachment', string = 'Attachment', ondelete = 'cascade')
    company_id = fields.Many2one('res.company')
    parent_id = fields.Many2one(
        'as.location',
        string='Parent',
        ondelete='restrict',
        index=True)
    child_ids = fields.One2many(
        'as.location', 'parent_id',
        string='Child')
    parent_path = fields.Char(index=True)

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError('Error! You cannot create recursive categories.')









