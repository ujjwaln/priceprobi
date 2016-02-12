__author__ = 'ujjwal'

_schema = {
    'name': {
        'type': 'string'
    },
    'unit': {
        'type': 'objectid',
        'required': True,
        'data_relation': {
            'resource': 'unit',
            'field': 'id',
            'embeddable': True
        }
    },
    'picture': {
        'type': 'string'
    }
}

Commodity = {
    'item_title': 'commodity',
    'resource_methods': ['GET', 'POST', 'DELETE'],
    'schema': _schema
}
