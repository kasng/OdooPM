# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
import uuid


class AttachmentsShare(models.Model):
    _name = 'attachments.share'
    _description = 'Attachments Share'

    def _default_access_token(self):
        return uuid.uuid4().hex

    def _compute_state(self):
        for record in self:
            record.state = 'live'
            if record.end_date:
                today = fields.Date.from_string(fields.Date.today())
                end_date = fields.Date.from_string(record.end_date)
                if (end_date - today).days <= 0:
                    record.state = 'expired'

    @api.depends('access_token')
    def _compute_url(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for record in self:
            record.url = "%s/attachment/share/%s/%s" % (base_url, record.id, record.access_token)

    name = fields.Char(string="Name")
    folder_id = fields.Many2one('folder.folder', requried=True)
    url = fields.Char(string="URL", compute='_compute_url', store=True)
    access_token = fields.Char('Token', default=_default_access_token)
    end_date = fields.Date(string="Valid Until")
    domain = fields.Char(string='Domain')
    state = fields.Selection([
        ('live', "Live"),
        ('expired', "Expired"),
    ], default='live', compute='_compute_state', string="Status")
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    type = fields.Selection([
        ('download', "Download"),
        ('downloadandupload', "Download and Upload"),
    ], default='download', string="Allows to")
    tag_ids = fields.Many2many('folder.tag', string="Shared Tags")
    partner_id = fields.Many2one('res.partner', string="Contact")
    user_id = fields.Many2one('res.users', string="Responsible Person", default=lambda self: self.env.user.id)

    @api.model
    def on_create_share(self, vals):
        share = self.create(vals)
        view_id = self.env.ref('sync_documents.share_form_popup_view').id
        return {
            'res_model': 'attachments.share',
            'target': 'new',
            'name': _('Share'),
            'res_id': share.id,
            'type': 'ir.actions.act_window',
            'views': [[view_id, 'form']],
        }
