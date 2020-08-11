# -*- coding: utf-8 -*-
{
    'name': "Asset Management System",  # Module title
    'summary': "",  # Module subtitle phrase
    'description': """""",  # You can also rst format
    'author': "DHA Vietnam",
    'website': "http://www.dha-tech.com.vn",
    'category': 'Asset',
    'version': '12.0.1',
    'depends': ['base', 'hr', 'stock'],
    # This data files will be loaded at the installation (commented becaues file is not added in this example)
    'data': [
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
}
