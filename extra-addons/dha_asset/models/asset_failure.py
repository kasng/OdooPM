# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AsFailRemedy(models.Model):
    _name = 'as.fail.remedy'
    _description = 'Remedy'

    name = fields.Char('Remedy', required=True)
    description = fields.Char('Description', required=True)
    cause_id = fields.Many2one('as.fail.cause', 'Cause', required=True)


class AsFailCause(models.Model):
    _name = 'as.fail.cause'
    _description = 'Cause'

    name = fields.Char('Cause', required=True)
    description = fields.Char('Description', required=True)
    remedy_ids = fields.One2many('as.fail.remedy', 'cause_id', 'Remedy')
    problem_id = fields.Many2one('as.fail.problem', 'Problem', required=True)


class AsFailProblem(models.Model):
    _name = 'as.fail.problem'
    _description = 'Problem'

    name = fields.Char('Problem', required=True)
    description = fields.Char('Description', required=True)
    cause_ids = fields.One2many('as.fail.cause', 'problem_id', 'Cause')
    class_id = fields.Many2one('as.fail.class', 'Class', required=True)


class AsFailClass(models.Model):
    _name = 'as.fail.class'
    _description = 'Class'

    name = fields.Char('Class', required=True)
    description = fields.Char('Description', required=True)
    problem_ids = fields.One2many('as.fail.problem', 'class_id', 'Problem')
