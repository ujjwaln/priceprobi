__author__ = 'ujjwal'

_schema = {

    'fbId': {
        'type': 'string'
    },

    'accessToken': {
        'type': 'string'
    },

    'appToken': {
        'type': 'string'
    },

    'expires': {
        'type': 'integer'
    },

    'roles': {
        'type': 'list'
    }
}

User = {

    'item_title': 'user',

    'additional_lookup': {
        'url': 'regex("[\d]+")',
        'field': 'fbId'
    },

    'resource_methods': ['GET', 'POST'],

    'schema': _schema
}
