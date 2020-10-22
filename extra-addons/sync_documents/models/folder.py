# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Folder(models.Model):
    _name = 'folder.folder'
    _description = 'Document Folder'
    _parent_name = 'parent_id'
    _inherit = 'document.thumbnail.mixins'

    def _compute_action_ids(self):
        for folder in self:
            folder.count_action = len(folder.action_ids)

    @api.depends('parent_id')
    def _compute_subfolders(self):
        for folder in self:
            folder.no_of_subfolders = folder.child_ids and len(folder.child_ids.ids) or 0

    @api.depends('file_ids', 'file_ids.folder_id')
    def _compute_files(self):
        tags_data = self.env['ir.attachment'].read_group([('folder_id', 'in', self.ids)], ['folder_id'], ['folder_id'])
        result = dict((data['folder_id'][0], data['folder_id_count']) for data in tags_data)
        for folder in self:
            folder.no_of_files = result.get(folder.id, 0)

    name = fields.Char(required=True, string='Name')
    parent_id = fields.Many2one('folder.folder', string="Parent Folder", ondelete="cascade")
    child_ids = fields.One2many('folder.folder', 'parent_id', string="Child Folders")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    access_type = fields.Selection([
        ('by_user', "By User"),
        ('by_group', "By Group"),
    ], default='by_user', string="Allow Access")
    group_ids = fields.Many2many('res.groups', string="Write Groups")
    read_group_ids = fields.Many2many('res.groups', relation='folder_read', string="Read Groups")
    user_ids = fields.Many2many('res.users', string='Users', default=lambda self: [self.env.user.id])
    tag_ids = fields.One2many('tag.tag', 'folder_id', string="Tags")
    description = fields.Html(string="Description")
    sequence = fields.Integer(string='Sequence')
    file_ids = fields.One2many('ir.attachment', 'folder_id', string="Files")
    no_of_subfolders = fields.Integer(compute='_compute_subfolders', string="Number of Tags",
            help='Number of tags currently occupying this Folder.')
    no_of_files = fields.Integer(compute='_compute_files', string="Number of Files", store=True,
                help='Number of files currently occupying this Folder.')
    action_ids = fields.One2many('document.action.rule', 'folder_id', string='Actions')
    count_action = fields.Integer(string='Total Action', compute='_compute_action_ids')
    project_id = fields.Many2one('project.project', 'Projects', required=False)

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError('You cannot create recursive Folders.')

    def _get_thumbnail_name(self):
        self.ensure_one()
        return "folder.png"

    def name_get(self):
        result = []
        hierarchical_naming = self.env.context.get('hierarchical_naming', True)
        for record in self:
            if hierarchical_naming and record.parent_id:
                result.append((record.id, "%s / %s" % (record.parent_id.name, record.name)))
            else:
                result.append((record.id, record.name))
        return result

    def show_actions(self):
        self.ensure_one()
        action_rules = self.action_ids
        action = self.env.ref('sync_documents.action_document_action_rule').read()[0]
        action['context'] = dict(
                default_folder_id=self.id,
                view_from_folder=1
            )
        action['domain'] = [('id', 'in', action_rules.ids)]
        if len(action_rules) == 1:
            form_view = [(self.env.ref('sync_documents.document_action_form_view').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = action_rules.id # `ensure_one`
        return action
