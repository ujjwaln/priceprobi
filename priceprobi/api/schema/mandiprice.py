__author__ = 'ujjwal'

_schema = {

    'arrival_date': {
        'type': 'string'
    },

    'district': {
        'type': 'string'
    },

    'state': {
        'type': 'string'
    },

    'market': {
        'type': 'string'
    },

    'commodity': {
        'type': 'string'
    },

    'min_price': {
        'type': 'float'
    },

    'max_price': {
        'type': 'float'
    },

    'modal_price': {
        'type': 'float'
    },

    'variety': {
        'type': 'float'
    },

    'cics_loc': {
        'type': 'point'
    },

}

MandiPrice = {

    'item_title': 'mandiprice',

    'resource_methods': ['GET', 'POST'],

    'schema': _schema,

    'datasource': {
        'source': 'mandi_prices'
    }
}
