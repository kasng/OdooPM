# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.osv import expression
from dateutil.relativedelta import relativedelta
from odoo.tools.safe_eval import safe_eval


class DocumentAction(models.Model):
    _name = 'document.action.rule'
    _description = 'Document Action Rule'

    def _get_create_model(self):
        for record in self:
            record.is_create_model = len(self._fields['create_model'].selection)

    name = fields.Char(string='Action Name', required=True)
    action_tooltip = fields.Char(string='Tooltip')
    user_id = fields.Many2one('res.users', string='Set Owner')
    folder_id = fields.Many2one('folder.folder', string='Current Folder')
    move_folder_id = fields.Many2one('folder.folder', string='Move to Folder')
    is_mark_done_activity = fields.Boolean(string='Mark All as Done', default=False)
    is_schedule_activity = fields.Boolean(string='Schedule Activity', default=False)
    activity_type_id = fields.Many2one('mail.activity.type', string="Activity type")
    is_create_model =  fields.Boolean(compute='_get_create_model')
    create_model = fields.Selection([], string='Create')
    activity_summary = fields.Char('Summary')
    activity_date_deadline_range = fields.Integer(string='Due Date In')
    activity_date_deadline_range_type = fields.Selection([
            ('days', 'Days'),
            ('weeks', 'Weeks'),
            ('months', 'Months'),
        ], string='Due type', default='days')
    activity_note = fields.Html(string="Activity Note")
    activity_user_id = fields.Many2one('res.users', string='Responsible')
    condition_folder_id = fields.Many2one('folder.folder', string='Folder')
    condition_type = fields.Selection([
            ('criteria', 'Criteria'),
            ('domain', 'Domain')
        ], default='criteria', string='Condition Type')
    domain = fields.Char(string="Domain", default="[]")
    criteria_partner_id = fields.Many2one('res.partner', string='Contact')
    criteria_owner_id = fields.Many2one('res.partner', string='Owner')
    document_action_ids = fields.One2many('document.action', 'action_id', string='Set Tags')
    included_tag_ids = fields.Many2many('folder.tag', 'document_action_rule_tag_rel',
        'rule_id', 'tag_id', string='Contains')
    excluded_tag_ids = fields.Many2many('folder.tag', 'document_action_rule_no_tag_rel',
        'rule_id', 'tag_id', string='Does not Contains')
    condition_user_id = fields.Many2one('res.users', string='Owner')

    project_id = fields.Many2one('project.project', string='Move to Project')

    def create_model_record(self, attachments):
        return True

    @api.model
    def get_action_rules(self, folder_id, attachments):
        IrAttachment = self.env['ir.attachment']
        folder_id = self.env['folder.folder'].browse(folder_id)
        rules = folder_id.action_ids    # self
        attachment_ids = IrAttachment.browse(attachments)
        attachments_per_rule = {rule: IrAttachment for rule in rules}
        def corresponding_attachments(rule):
            if rule.condition_type == 'criteria':

                check_included_tags = lambda att: ((not rule.included_tag_ids) or\
                    ((rule.included_tag_ids and att.tag_ids) and\
                    (bool(set(att.tag_ids.ids).intersection(set(rule.included_tag_ids.ids))))))

                check_excluded_tags = lambda att: (not rule.excluded_tag_ids) or\
                    ((rule.excluded_tag_ids and att.tag_ids) and\
                    (not set(att.tag_ids.ids).intersection(set(rule.excluded_tag_ids.ids))))

                check_user = lambda att: ((not rule.condition_user_id) or\
                    ((rule.condition_user_id and att.user_id) and\
                    (rule.condition_user_id.id == att.user_id.id)))

                return attachment_ids.filtered(
                        lambda att: check_included_tags(att) and check_excluded_tags(att) and check_user(att)
                    )
            elif rule.condition_type == 'domain':
                return IrAttachment.search(expression.AND([
                        safe_eval(rule.domain),
                        [('id', 'in', attachment_ids.ids)]
                    ]))

        for rule in rules:
            attachments_per_rule[rule] += corresponding_attachments(rule)

        for rule, attachments in attachments_per_rule.items():
            if set(attachment_ids.ids).symmetric_difference(set(attachments.ids)):
                rules -= rule

        return [{'id': rule.id, 'name': rule.name} for rule in rules]

    def action_execute(self, attachments):
        self.ensure_one()
        attachment_ids = self.env['ir.attachment'].browse(attachments)
        vals = dict()   # tag_ids=[(6, 0, [])]
        if self.user_id:
            vals.update(user_id=self.user_id.id)
        if self.move_folder_id:
            vals.update(folder_id=self.move_folder_id.id)
        if self.project_id:
            # write project id into dha.document
            for att in attachments:
                dha_document = self.env['dha.document'].search([('attachment_id', '=', att)], limit=1)
                if dha_document:
                    dha_document.write({
                        'project_id': self.project_id.id,
                        'moved_date': fields.Datetime.now()
                    })
                else:
                    # Create new
                    self.env['dha.document'].create({
                        'project_id': self.project_id.id,
                        'moved_date': fields.Datetime.now(),
                        'attachment_id': att
                    })

        attachment_ids.write(vals)

        if self.is_mark_done_activity:
            attachment_ids.mapped('activity_ids').action_feedback(
                feedback="completed by action: %s. %s" % (self.name, self.action_tooltip or '')
            )

        if self.is_schedule_activity:
            activity_vals = {
                'user_id': self.activity_user_id.id if self.activity_user_id else self.env.user.id,
                'activity_type_id': self.activity_type_id.id if self.activity_type_id else False,
                'note': self.activity_note,
            }
            if self.activity_date_deadline_range > 0:
                activity_vals['date_deadline'] = fields.Date.context_today(self) + relativedelta(**{
                        self.activity_date_deadline_range_type: self.activity_date_deadline_range
                    })
            for attachment in attachment_ids:
                attachment.activity_schedule(**activity_vals)

        self.document_action_ids.action_tags(attachment_ids)

        if self.create_model:
            self.create_model_record(attachment_ids)

        return True

    def get_corresponding_records(self, attachment_id):
        attachment = self.env['ir.attachment'].browse(attachment_id)
        related_records = list()
        if attachment.res_model and attachment.res_id:
            related_records = self.env[attachment.res_model].search_read(
                [('id', '=', attachment.res_id)],
                ['display_name']
            )
            for rec in related_records:
                rec.update(res_model=attachment.res_model)
        return related_records


class DocumentWorkflowAction(models.Model):
    _name = 'document.action'
    _description = 'Action Action'

    action_id = fields.Many2one('document.action.rule', string='Action')
    action = fields.Selection([
        ('add', "Add"),
        ('replace', "Replace by"),
        ('remove', "Remove"),
    ], default='add', required=True)

    category_tag_id = fields.Many2one('tag.tag', string="Category")
    folder_tag_id = fields.Many2one('folder.tag', string="Tag")

    def action_tags(self, attachments):
        FolderTag = self.env['folder.tag']
        for rec in self:
            move_folder_id = rec.action_id.move_folder_id
            if rec.action == "add" and rec.folder_tag_id:
                attachments.write({'tag_ids': [(4, rec.folder_tag_id.id, False)]})
            elif rec.action == "replace" and rec.category_tag_id:
                vals_to_write = [(3, tag.id, False) for tag in (rec.category_tag_id.tag_ids - rec.folder_tag_id)]
                if rec.folder_tag_id:
                    vals_to_write.append([(4, rec.folder_tag_id.id, False)])
                attachments.write({'tag_ids': vals_to_write})
            elif rec.action == "remove":
                attachments.write({'tag_ids': [(3, tag.id, False) for tag in (rec.category_tag_id.tag_ids + rec.folder_tag_id)]})
        return True
