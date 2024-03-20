{
    'name': 'PLM - Ciclo de vida de produto',
    'version': '1.0',
    'description': 'Ciclo de vida de produto',
    'summary': 'Ciclo de vida de produto',
    'author': 'DevFazer',
    'website': 'defazer.com.br',
    'license': 'LGPL-3',
    'category': 'product',
    'depends': [
        'base',
        'sale'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/sale_order_views.xml',
        'views/plm_views.xml'
    ],
    'auto_install': False,
    'application': True,
}