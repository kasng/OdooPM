# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from dateutil.relativedelta import relativedelta

class AttachmentRequestWizard(models.TransientModel):
    _name = "attachment.request"
    _description = "Document Request"

    name = fields.Char(required=True)
    tag_ids = fields.Many2many('folder.tag', string="Tags")
    folder_id = fields.Many2one('folder.folder')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user.id, string="Responsible Person")
    activity_type_id = fields.Many2one('mail.activity.type', string="Activity type",
                                           default=lambda self: self.env.ref('sync_documents.activity_requested_attachment'))
    activity_note = fields.Html(string="Note")
    activity_date = fields.Integer(string='Due Date In')
    activity_date_type = fields.Selection([
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
    ], string='Due type', default='days')

    def request_for_document(self):
        self.ensure_one()
        attachment_obj = self.env['ir.attachment']
        attachment = attachment_obj.create({
            'name': self.name,
            'user_id': self.user_id.id if self.user_id else False,
            'type': 'empty',
            'tag_ids': [(6, 0, self.tag_ids.ids if self.tag_ids else [])],
            'folder_id': self.folder_id.id if self.folder_id else False,
        })
        vals = {
            'user_id': self.user_id.id if self.user_id else self.env.user.id,
            'activity_type_id': self.activity_type_id.id if self.activity_type_id else False,
            'note': self.activity_note,
        }
        if self.activity_date > 0:
            vals['date_deadline'] = fields.Date.context_today(self) + relativedelta(**{self.activity_date_type: self.activity_date})

        attachment.activity_schedule(**vals)
