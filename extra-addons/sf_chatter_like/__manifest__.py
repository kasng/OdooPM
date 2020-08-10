{
    'name': "Chatter Like",
    'author': 'sf',
    'version': '12.0.1.0.0',
    'maintainer': 'dungtv',
    'category': 'Chatter',
    'sequence': 1000,
    'summary': """Chatter Like""",
    'depends': ['base', 'web', 'mail'],
    'data': [
        'views/assets.xml',
    ],
    'demo': [
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'application': True,
}
