# -*- coding: utf-8 -*-
{
    'name': "Asset Management System",

    'summary': "",

    'description': "",

    'author': "DHA Vietnam",
    'website': "http://www.dha-tech.com.vn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Asset',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/asset_config.xml',
        'views/asset_location.xml',
        'views/asset_asset.xml',
        'views/asset_service.xml',
        'views/asset_work.xml',
        'views/asset_failure.xml',
        'views/asset_history.xml',
        'views/asset_menu.xml',
        'wizard/enter_meter_wizard.xml',
        'wizard/enter_expense_wizard.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
