from odoo import api, fields, models, tools, SUPERUSER_ID, _
import ast


class DHAProject(models.Model):
    _inherit = "project.project"

    # sync_doc_count = fields.Integer(compute='_compute_syned_docs_count', string="Number of sync documents attached")

    def attachment_tree_view(self):
        attachment_action = self.env.ref('sync_documents.action_document_dashboard')
        action = attachment_action.read()[0]
        action['domain'] = str([
            '|',
            '&',
            ('res_model', '=', 'project.project'),
            ('res_id', 'in', self.ids),
            '&',
            ('res_model', '=', 'project.task'),
            ('res_id', 'in', self.task_ids.ids)
        ])
        action['context'] = "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)

        action['display_name'] = _('Documents')
        domain = ast.literal_eval(action['domain'])
        # Get data from dha_document
        dha_documents = self.env['ir.attachment'].search([('project_ids', '=', self.id)])
        if dha_documents:
            domain.insert(0, '|')
            domain.append(('id', 'in', dha_documents.ids))
            action['domain'] = str(domain)

        return action

        action = super(DHAProject, self).attachment_tree_view()
        action['display_name'] = _('Documents')
        domain = ast.literal_eval(action['domain'])
        # Get data from dha_document
        dha_documents = self.env['ir.attachment'].search([('project_ids', '=', self.id)])
        if dha_documents:
            domain.insert(0, '|')
            domain.append(('id', 'in', dha_documents.ids))
            action['domain'] = str(domain)
        return action

    # def _compute_syned_docs_count(self):
    #     Attachment = self.env['ir.attachment']
    #     dha_documents = self.env['dha.document'].search([('project_id', '=', self.id)])
    #     for project in self:
    #         project.sync_doc_count = Attachment.search_count([
    #             ('id', 'in', dha_documents.attachment_id.ids)
    #         ])

    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        dha_documents = self.env['ir.attachment'].search([('project_ids', '=', self.id)])
        for project in self:
            project.doc_count = Attachment.search_count([
                '|',
                '|',
                '&',
                ('res_model', '=', 'project.project'), ('res_id', '=', project.id),
                '&',
                ('res_model', '=', 'project.task'), ('res_id', 'in', project.task_ids.ids),
                ('id', 'in', dha_documents.ids)
            ])
