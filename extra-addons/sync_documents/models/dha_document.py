# -*- coding: utf-8 -*-

from odoo import api, fields, models


class DHADocument(models.Model):
    _name = "dha.document"

    attachment_id = fields.Many2one('ir.attachment', string='Related attachment', required=True)
    project_id = fields.Many2one('ir.attachment', string='Project attachment')
    moved_date = fields.Datetime('Moved Date', default=lambda self: fields.Datetime.now())