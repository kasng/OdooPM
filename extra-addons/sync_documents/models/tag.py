# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.osv import expression


class Tag(models.Model):
    _name = 'tag.tag'
    _description = "Tag"
    _order = "sequence"

    name = fields.Char(required=True, string='Name')
    tag_ids = fields.One2many('folder.tag', 'tag_id', string="Child Tag")
    folder_id = fields.Many2one('folder.folder', ondelete="cascade")
    sequence = fields.Integer(string='Sequence')

    _sql_constraints = [
        ('name_unique', 'unique (folder_id, name)', "Tag name must be unique per folder!"),
    ]


class FolderTag(models.Model):
    _name = 'folder.tag'
    _description = 'Folder Tags'

    name = fields.Char(string='Name', required=True)
    folder_id = fields.Many2one('folder.folder', related='tag_id.folder_id', store=True, string="Folder")
    tag_id = fields.Many2one('tag.tag', string="Folder Tag", ondelete='cascade', required=True)
    sequence = fields.Integer(string='Sequence')
    color = fields.Integer(string='Color Index', default=0)

    _sql_constraints = [
        ('name_tag_uniq', 'unique (tag_id, name)', "Tag name already exists in this main tag!"),
    ]

    @api.model
    def get_tags(self, default_folder_id, domain=[]):
        folders = self.env['folder.folder'].search([('parent_id', 'parent_of', default_folder_id)])
        attachments = self.env['ir.attachment'].search(expression.AND([domain, [('folder_id', '=', default_folder_id)]]))
        args = [tuple(folders.ids), list(attachments.ids)]
        where_clause = """
            FROM folder_tag
                JOIN tag_tag tag ON folder_tag.tag_id = tag.id AND tag.folder_id IN %s
                LEFT JOIN rel_folder_tag rel ON folder_tag.id = rel.folder_tag_id AND rel.ir_attachment_id = ANY(%s)
                GROUP BY tag.sequence, tag.id, tag.name, folder_tag.sequence, folder_tag.id, folder_tag.name
                ORDER BY tag.sequence, tag.id, tag.name, folder_tag.sequence, folder_tag.id, folder_tag.name
        """
        query = """
            SELECT tag.sequence AS group_sequence,
                    tag.name AS group_name,
                    tag.id AS group_id,
                    tag.name AS group_tooltip,
                    folder_tag.sequence AS sequence,
                    folder_tag.name AS name,
                    folder_tag.id AS id,
                    COUNT(rel.ir_attachment_id) AS count
            %s
            """ % (where_clause)
        self._cr.execute(query, args)
        return self._cr.dictfetchall()
