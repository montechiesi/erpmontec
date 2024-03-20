# -*- coding: utf-8 -*-
{
    'license': 'LGPL-3',
    'name': "Web Window Title",
    'summary': "The custom web window title",
    'author': "renjie <i@renjie.me>",
    'website': "https://renjie.me",
    'support': 'i@renjie.me',
    'category': 'Extra Tools',
    'version': '1.1',
    'depends': ['base', 'web'],
    'demo': [
        'data/demo.xml',
    ],
    'data': [
        'views/res_config.xml',
       # 'views/webclient_inherit.xml',
    ],
    'images': [
        'static/description/main_screenshot.png',
    ],
    'assets': {
        'web.assets_backend': [
            'web_window_title/static/src/js/web_window_title.js',
        ],
        # 'web.assets_common': [
        #     'web_window_title/static/src/js/**/*',
        # ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
