from odoo import api, fields, models, tools, SUPERUSER_ID, _
import ast


class DHAProject(models.Model):
    _inherit = "project.project"

    sync_doc_count = fields.Integer(compute='_compute_syned_docs_count', string="Number of sync documents attached")

    def attachment_tree_view(self):
        action = super(DHAProject, self).attachment_tree_view()
        action['display_name'] = _('Documents')
        domain = ast.literal_eval(action['domain'])
        # Get data from dha_document
        dha_documents = self.env['dha.document'].search([('project_id', '=', self.id)])
        if dha_documents:
            domain.insert(0, '|')
            domain.append(('id', 'in', dha_documents.attachment_id.ids))
            action['domain'] = str(domain)
        return action

    def _compute_syned_docs_count(self):
        Attachment = self.env['ir.attachment']
        dha_documents = self.env['dha.document'].search([('project_id', '=', self.id)])
        for project in self:
            project.sync_doc_count = Attachment.search_count([
                ('id', 'in', dha_documents.attachment_id.ids)
            ])

    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        dha_documents = self.env['dha.document'].search([('project_id', '=', self.id)])
        for project in self:
            project.doc_count = Attachment.search_count([
                '|',
                '|',
                '&',
                ('res_model', '=', 'project.project'), ('res_id', '=', project.id),
                '&',
                ('res_model', '=', 'project.task'), ('res_id', 'in', project.task_ids.ids),
                ('id', 'in', dha_documents.attachment_id.ids)
            ])
