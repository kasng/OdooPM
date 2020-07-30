# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.osv import expression
from odoo import api, fields, models


class IrAttachment(models.Model):
    _name = 'ir.attachment'
    _inherit = ['ir.attachment', 'document.thumbnail.mixins', 'mail.thread', 'mail.activity.mixin']

    folder_id = fields.Many2one('folder.folder', string="Folder", track_visibility='onchange')
    tag_ids = fields.Many2many('folder.tag', 'rel_folder_tag', string="Tags", domain="[('folder_id', '=', folder_id)]")
    extension = fields.Char(compute='_compute_extension', string='Extension', readonly=True, store=True)
    type = fields.Selection(selection_add=[('empty', "Empty")])
    active = fields.Boolean(default=True)
    starred_ids = fields.Many2many('res.users', string="Starred")
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user.id, string="Resposible Person")

    @api.onchange('folder_id')
    def onchange_folder_id(self):
        if self.folder_id:
            self.tag_ids = [(6, 0, [])]

    def attachment_url(self):
        return True

    @api.depends('name')
    def _compute_extension(self):
        for record in self:
            record.extension = record.mimetype and record.mimetype.split('/')[1]

    def _get_thumbnail_name(self):
        self.ensure_one()
        return self.extension and "file_%s.png" % self.extension or ""

    def toggle_starred(self):
        self.ensure_one()
        for record in self:
            if record.env.user in self[0].starred_ids:
                record.starred_ids = [(3, record.env.user.id)]
            else:
                record.starred_ids = [(4, record.env.user.id)]

    def _config_settings(self):
        return True

    @api.model_create_multi
    def create(self, vals_list):
        resources = super(IrAttachment, self).create(vals_list)
        for resource in resources.filtered(lambda record: record.res_model): 
            resource._config_settings()
        return resources

    @api.model
    def search_panel_select_range(self, field_name):
        return super(IrAttachment, self.with_context(hierarchical_naming=False)).search_panel_select_range(field_name)

    @api.model
    def search_panel_select_multi_range(self, field_name, **kwargs):
        category_domain = kwargs.get('category_domain', [])
        if field_name == 'tag_ids':
            folder_id = category_domain[0][2] if len(category_domain) else []
            if folder_id:
                domain = expression.AND([
                    kwargs.get('search_domain', []), category_domain, kwargs.get('filter_domain', []),
                    [(field_name, '!=', False)],
                ])
                return self.env['folder.tag'].get_tags(folder_id, domain)
            else:
                return []
        return super(IrAttachment, self).search_panel_select_multi_range(field_name, **kwargs)