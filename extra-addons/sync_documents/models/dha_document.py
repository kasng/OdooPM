# -*- coding: utf-8 -*-

from odoo import api, fields, models


class DHADocument(models.Model):
    _name = "dha.document"

    attachment_id = fields.Many2one('ir.attachment', string='Related attachment')
    project_id = fields.Many2many('project.project', string='Project attachment')
    moved_date = fields.Datetime('Moved Date', default=lambda self: fields.Datetime.now())

    @api.model
    def create(self, vals_list):
        print(vals_list)
        if self._context.get('selectedDocuments'):
            records = []
            for _doc in self._context.get('selectedDocuments'):
                new_vals = dict()
                new_vals.update(attachment_id=_doc, project_id=vals_list.get('project_id'))
                records.append(super(DHADocument, self).create(new_vals))
            return records[0]
        else:
            return super(DHADocument, self).create(vals_list)
