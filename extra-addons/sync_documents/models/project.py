from odoo import api, fields, models, tools, SUPERUSER_ID, _
import ast


class DHAProject(models.Model):
    _inherit = "project.project"

    sync_doc_count = fields.Integer(compute='_compute_syned_docs_count', string="Number of sync documents attached")

    def sync_attachment_tree_view(self):
        attachment_action = self.env.ref('sync_documents.action_document_dashboard')
        action = attachment_action.read()[0]
        # Get data from dha_document
        dha_documents = self.env['dha.document'].search([('project_id', '=', self.id)])
        action['domain'] = str([
            ('id', 'in', dha_documents.attachment_id.ids),
        ])
        action['context'] = "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        action['display_name'] = _('Operation Documents')
        return action

    def attachment_tree_view(self):
        action = super(DHAProject, self).attachment_tree_view()
        action['display_name'] = _('Documents')
        # domain = ast.literal_eval(action['domain'])
        # # Get data from dha_document
        # dha_documents = self.env['dha.document'].search([('project_id', '=', self.id)])
        # if dha_documents:
        #     domain.insert(0, '|')
        #     domain.append(('id', 'in', dha_documents.attachment_id.ids))
        #     action['domain'] = str(domain)
        return action

    def _compute_syned_docs_count(self):
        Attachment = self.env['ir.attachment']
        dha_documents = self.env['dha.document'].search([('project_id', '=', self.id)])
        for project in self:
            project.sync_doc_count = Attachment.search_count([
                ('id', 'in', dha_documents.attachment_id.ids)
            ])
