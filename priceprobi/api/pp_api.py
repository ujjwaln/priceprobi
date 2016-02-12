__author__ = 'ujjwal'

from flask import make_response, request, jsonify, json
from eve import Eve
from priceprobi.utils import get_env
from priceprobi.config import get_config
from auth import get_pp_user
from priceprobi.utils import get_magic_user, Encoder
from . import crossdomain


env = get_env()
api_settings = get_config(env)
#app = Eve(settings=api_settings, auth=CfApiBasicAuth())
app = Eve(settings=api_settings)
app.json_encoder = Encoder


def _mandiprices_geojson(_items):
    features = []
    for _item in _items:
        if "cics_loc" in _item:
            properties = {
                "_id": str(_item["_id"]),
                "arrival_date": _item["arrival_date"],
                "commodity": _item["commodity"],
                "district": _item["district"],
                "market": _item["market"],
                "max_price": _item["max_price"],
                "min_price": _item["min_price"],
                "modal_price": _item["modal_price"],
                "state": _item["state"],
                "variety": _item["variety"]
            }

            feature = {
                "type": "Feature",
                "properties": properties,
                "geometry": _item["cics_loc"]
            }

            features.append(feature)

    layer = {
        "type": "FeatureCollection",
        "features": features
    }

    return layer


def post_GET_mandiprice_callback(request, payload):
    fmt = request.args.get("format")
    if fmt == "geojson":
        obj = json.loads(payload.data)
        layer = _mandiprices_geojson(obj["_items"])
        obj["_items"] = layer
        resp = json.dumps(obj)
        payload.data = resp


def fetched_resource_mandiprice_callback(resp):
    pass

app.on_post_GET_mandiprice += post_GET_mandiprice_callback
#app.on_fetched_resource_mandiprice += fetched_resource_mandiprice_callback


@app.route('/distinct_commodities', methods=['GET'])
@crossdomain(origin="*", methods=["GET"])
def distinct_commodities():
    ctx = app.data.driver.db['mandi_prices']
    results = ctx.distinct("commodity")
    resp = jsonify({"commodities": results})
    return make_response(resp)


@app.route('/auth/token', methods=['POST', 'OPTIONS'])
def auth_token():
    if request.method == 'POST' and request.json:
        try:
            access_token = request.json.get('accessToken')
            fb_id = request.json.get('fbId')
            roles = request.json.get('roles')
            user = get_pp_user(fb_id, access_token, roles)
            user_json = jsonify({"user": user})
            resp = make_response(user_json)
        except Exception:
            resp = make_response()
    else:
        resp = app.make_default_options_response()

    resp.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Max-Age'] = '60'
    resp.headers['Content-Type'] = 'application/json; charset=UTF-8'
    resp.headers['Access-Control-Allow-Headers'] = 'origin, content-type, accept'

    return resp


@app.route('/insert_test_data', methods=['POST', 'OPTIONS'])
def insert_test_data():

    """ checks if dev/test db has magic user, otherwise insert it"""
    magic_user = get_magic_user()
    ctx = app.data.driver.db['user']
    user = ctx.find_one({"fbId": magic_user["fbId"]})
    if user:
        ctx.update({'_id': user['_id']}, magic_user)
    else:
        user_id = ctx.insert(magic_user)
        user = ctx.find_one({'_id': user_id})
    #resp = json.dumps({"user": user}, cls=Encoder)
    resp = jsonify({"user": user})

    return make_response(resp)


if __name__ == '__main__':
    host = api_settings['SERVICE_HOST']
    port = api_settings['SERVICE_PORT']

    #run the app
    app.run(host=host, port=port)
