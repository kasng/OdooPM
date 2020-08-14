from odoo import api, fields, models, tools, SUPERUSER_ID, _
import ast

class DHAProject(models.Model):
    _inherit = "project.project"

    def attachment_tree_view(self):
        action = super(DHAProject, self).attachment_tree_view()
        domain = ast.literal_eval(action['domain'])
        # Get data from dha_document
        dha_documents = self.env['dha.document'].search([('project_id', '=', self.id)])
        if dha_documents:
            domain.insert(0, '|')
            domain.append(('id', 'in', dha_documents.attachment_id.ids))
            action['domain'] = str(domain)
        return action
