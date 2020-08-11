# -*- coding: utf-8 -*-
from odoo import models, fields


class AsEnterExpenseWizard(models.TransientModel):
    _name = 'as.enter.expense.wizard'

    name = fields.Char('Expense Entry')
    asset_id = fields.Many2one('as.asset', string='Asset', readonly=True)
    asset_description = fields.Char(string='Description', related='asset_id.description')
    expense_type = fields.Selection(
        [('fuel', 'Fuel Entry'),
         ('tolls', 'Tolls Entry'),
         ('service', 'Service'),
         ('work_order', 'Work Order'),
         ('registration', 'Registration'),
         ('insurance', 'Insurance'),
         ('miscellaneous', 'Miscellaneous')],
        string='Expense Type', default='fuel')
    expense_entry = fields.Float('Expense (VND)')
    expense_time = fields.Datetime('Expense Time')
    inspector_id = fields.Many2one('hr.employee', string='Inspector', readonly=True)

    def save_expense_entry(self):
        self.ensure_one()
        expense_obj = self.env['as.expense.his']
        for r in self:
            if r.expense_entry:
                expense_obj.create({
                    'asset_id': self._context.get('asset_id', False),
                    'expense_type': r.expense_type,
                    'expense_entry': r.expense_entry,
                    'expense_time': r.expense_time,
                    'inspector_id': (r.inspector_id.id or False)
                })
        return True





