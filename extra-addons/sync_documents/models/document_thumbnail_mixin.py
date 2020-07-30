# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import os
import base64

from odoo import models, fields, api
from odoo.modules.module import get_resource_path


class DocumentsThumbnail(models.AbstractModel):
    _name = 'document.thumbnail.mixins'
    _description = 'Document Thumbnail Mixin'

    custom_thumbnail = fields.Binary(string="Custom Thumbnail", attachment=False, prefetch=False)
    custom_thumbnail_medium = fields.Binary(string="Custom Medium Thumbnail", attachment=False, prefetch=False)
    custom_thumbnail_small = fields.Binary(string="Custom Small Thumbnail", attachment=False, prefetch=False)
    thumbnail = fields.Binary(compute='_compute_thumbnail', string="Thumbnail")
    thumbnail_medium = fields.Binary(compute='_compute_thumbnail_medium', string="Medium Thumbnail")
    thumbnail_small = fields.Binary(compute='_compute_thumbnail_small', string="Small Thumbnail")

    @api.model
    def _get_thumbnail_path(self, size, name):
        path = get_resource_path('sync_documents', 'static/src/img', size, name)
        if not os.path.isfile(path):
            path = get_resource_path('sync_documents', 'static/src/img', size, "file_unkown.png")
        return path

    @api.model
    def _check_context_bin_size(self, field):
        return any(key in self.env.context for key in ['bin_size', 'bin_size_%s' % (field)])

    @api.model
    def _get_thumbnail_placeholder(self, field, size, name):
        if self._check_context_bin_size(field):
            return os.path.getsize(self._get_thumbnail_path(size, name))
        else:
            path = self._get_thumbnail_path(size, name)
            with open(path, "rb") as image:
                return base64.b64encode(image.read())

    def _get_thumbnail_name(self):
        self.ensure_one()
        return "file_unkown.png"

    @api.depends('custom_thumbnail')
    def _compute_thumbnail(self):
        for record in self:
            if record.custom_thumbnail:
                record.thumbnail = record.custom_thumbnail
            else:
                record.thumbnail = self._get_thumbnail_placeholder(
                    'thumbnail', 'original', record._get_thumbnail_name()
                )

    @api.depends('custom_thumbnail_medium')
    def _compute_thumbnail_medium(self):
        for record in self:
            if record.custom_thumbnail_medium:
                record.thumbnail_medium = record.custom_thumbnail_medium
            else:
                record.thumbnail_medium = self._get_thumbnail_placeholder(
                    'thumbnail_medium', 'medium', record._get_thumbnail_name()
                )

    @api.depends('custom_thumbnail_small')
    def _compute_thumbnail_small(self):
        for record in self:
            if record.custom_thumbnail_small:
                record.thumbnail_small = record.custom_thumbnail_small
            else:
                record.thumbnail_small = self._get_thumbnail_placeholder(
                    'thumbnail_small', 'small', record._get_thumbnail_name()
                )
