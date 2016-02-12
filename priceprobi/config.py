__author__ = 'ujjwal'
import os
from priceprobi.api.schema.commodity import Commodity
from priceprobi.api.schema.user import User
from priceprobi.api.schema.pricereport import PriceReport
from priceprobi.api.schema.mandiprice import MandiPrice


OGD = {
    "api_url": r'https://data.gov.in/api/datastore/resource.json',
    "api_key": r'cf6a64f53fc6185c95b2146cc321196c',
    "mandi_prices_resource_id": r'9ef84268-d588-465a-a308-a864a43d0070',
    "mandi_prices_xml_url": "https://data.gov.in/sites/default/files/Date-Wise-Prices-all-Commodity.xml"
}

data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")

NOMINATIM = {
    "api_url": "http://open.mapquestapi.com/nominatim/v1/search.php"
}

CSIS = {
    "api_url": "http://india.csis.u-tokyo.ac.jp/geocode-cgi/census_ajax_json.cgi",
    "scraped_file_name": os.path.join(data_dir, 'csis_st_dist_subdist_data.json')
}

BasicConfig = {
    'MONGO_HOST': 'localhost',
    'MONGO_PORT': 27017,
    'DOMAIN': {
        'user': User,
        'commodity': Commodity,
        'pricereport': PriceReport,
        'mandiprice': MandiPrice
    },
    'RESOURCE_METHODS': ['GET', 'POST', 'DELETE', 'PUT'],
    'ITEM_METHODS': ['GET', 'PATCH', 'DELETE', 'PUT'],
    'CACHE_CONTROL': 'max-age=20',
    'CACHE_EXPIRES': 20,
    'X_DOMAINS': '*',
    'X_HEADERS': ["Origin, X-Requested-With, Content-Type, Accept, Authorization"],
    'ALLOWED_FILTERS': ['*'],
    'UPLOAD_FOLDER': 'uploads',
    'ENABLE_FB_ACCESS_TOKEN_CHECK': False,
    'XML': False,
    'JSON': True,
    'PAGINATION': False
}

ProductionConfig = {
    'ENVIRONMENT': 'PRODUCTION',
    'DEBUG': False,
    'TESTING': False,
    'MONGO_DBNAME': 'pp_prod',
    'MONGO_ADMIN_DBNAME': 'pp_admin_prod',
    'SERVER_NAME': None,
    'SERVICE_HOST': '0.0.0.0',
    'SERVICE_PORT': 8000
}

DevelopmentConfig = {
    'ENVIRONMENT': 'DEVELOPMENT',
    'DEBUG': True,
    'TESTING': True,
    'MONGO_DBNAME': 'pp_dev',
    'MONGO_ADMIN_DBNAME': 'pp_admin_dev',
    'OGD_DBNAME': 'ogd_dev',
    'SERVER_NAME': None,
    'SERVICE_HOST': '127.0.0.1',
    'SERVICE_PORT': 8000
}

TestConfig = {
    'ENVIRONMENT': 'TEST',
    'DEBUG': True,
    'TESTING': True,
    'MONGO_DBNAME': 'pp_test',
    'MONGO_ADMIN_DBNAME': 'pp_admin_test',
    'OGD_DBNAME': 'ogd_test',
    'SERVER_NAME': None,
    'SERVICE_HOST': '127.0.0.1',
    'SERVICE_PORT': 7000
}


def get_config(env='DEVELOPMENT'):
    if env == 'PRODUCTION':
        instance = dict(BasicConfig)
        instance.update(ProductionConfig)
        return instance

    elif env == 'TEST':
        instance = dict(BasicConfig)
        instance.update(TestConfig)
        return instance

    elif env == 'DEVELOPMENT':
        instance = dict(BasicConfig)
        instance.update(DevelopmentConfig)
        return instance

    else:
        raise Exception('specify PRODUCTION, TEST or DEVELOPMENT environment')
