# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AsServiceType(models.Model):
    _name = 'as.service.type'
    _description = 'Service Type'

    name = fields.Char('Service Type', required=True)
    description = fields.Char('Description',required=True)


class AsServiceGroup(models.Model):
    _name = 'as.service.group'
    _description = 'Service Group'

    name = fields.Char('Service Group', required=True)
    description = fields.Char('Description',required=True)









