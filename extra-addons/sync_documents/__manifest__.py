# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Document Management System',
    'version': '1.1',
    'summary': """
        This application is used to track, manage and store documents and reduce paper
    """,
    'category': "Operations/Documents",
    'sequence': 1,
    'description': """
Document management
=================
Manage Documents in Odoo.
    """,
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'depends': ['base', 'mail', 'portal', 'web', 'project'],
    'data': [
        'data/documents_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/folder_views.xml',
        'views/tag_views.xml',
        'views/document_actions_view.xml',
        'views/ir_attachment_views.xml',
        'views/assets.xml',
        'views/attachments_share_views.xml',
        'views/template.xml',
        'views/res_config_setting_view.xml',
        'wizard/attachment_request_views.xml',
    ],
     'qweb': [
         "static/src/xml/*.xml",
     ],
    'images': [
        'static/description/main_screen.png'
    ],
    'price': 210.0,
    'currency': 'EUR',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
}
