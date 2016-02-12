__author__ = 'ujjwal'

_schema = {

    'commodity': {
        'type': 'objectid',
        'required': True,
        'data_relation': {
            'resource': 'commodity',
            'field': '_id',
            'embeddable': True
        }
    },

    'user': {
        'type': 'objectid',
        'required': True,
        'data_relation': {
            'resource': 'user',
            'field': '_id',
            'embeddable': True
        }
    },

    'price': {
        'type': 'number',
        'required': True
    },

    'location': {
        'type': 'string'
    },

    'time': {
        'type': 'datetime',
        'required': True
    }
}

PriceReport = {

    'item_title': 'pricereport',

    'resource_methods': ['GET', 'POST'],

    'item_methods': ['GET', 'PATCH', 'DELETE'],

    'schema': _schema
}

