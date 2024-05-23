{
    'name': 'Export Current View',
    'version': '8.0.1.3.1',
    'category': 'Web',
    'license': 'AGPL-3',
    'depends': [
        'web',
    ],
    'data': [
        'view/web_export_view.xml',
    ],
    'qweb': [
        'static/src/xml/web_export_view_template.xml',
    ],
    'installable': True,
    'auto_install': False,
}
