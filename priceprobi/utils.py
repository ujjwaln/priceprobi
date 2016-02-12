__author__ = 'ujjwal'
import os
import urllib
import urllib2
import flask
import datetime
from bson import ObjectId


def get_env():
    if 'ENVIRONMENT' in os.environ:
        return str(os.environ['ENVIRONMENT']).upper()
    elif 'environment' in os.environ:
        return str(os.environ['environment']).upper()
    else:
        return "DEVELOPMENT"
        #raise Exception("ENVIRONMENT must be set to DEVELOPMENT, PRODUCTION or TEST")


def get_magic_user():
    fbId = '12622554'
    accessToken = "CAAGkwd2ejOoBAOmTiB1se6M0buz1nhpyvFE69olOa3x2RAaVSMKEbf6jIo8tHgr3jZBWEuX17TwZAXbTYQJ1HZBktw" + \
                "4lyXZAaQoEkZBe66AbnLfs4xZCNviTqvWWrIkKpwQQZCdqUIJod0jzD36sLMohdy3vClEiaBKQBiZAJ4WdlEpXEKI81gg8"
    cfToken = "CAAGkwd2ejOoBAOmTiB1se6M0buz1nhpyvFE69olOa3x2RAaVSMKEbf6jIo8tHgr3jZBWEuX17TwZAXbTYQJ1HZBktw"
    expires = 5180903
    roles = ["user"]

    return {
        'fbId': fbId,
        'accessToken': accessToken,
        'cfToken': cfToken,
        'expires': expires,
        'roles': roles
    }


def get_json(url, params, auth):
    if params:
        url = url + "?" + urllib.urlencode(params)

    req = urllib2.Request(url, None)
    if auth:
        req.add_header('Authorization', auth)
    try:
        f = urllib2.urlopen(req)
        response = f.read()
        f.close()
        return response
    except:
        print 'Error in get_json %s' % url
        raise


class Encoder(flask.json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)

        if isinstance(obj, unicode):
            return str(obj)

        elif isinstance(obj, datetime.datetime):
            #Thu, 27 Aug 1970 14:37:13 GMT
            if obj.utcoffset() is not None:
                obj = obj - obj.utcoffset()
                formatted_time = obj.strftime('%a, %d %b %Y %H:%M:%S %Z')
            else:
                formatted_time = obj.strftime('%a, %d %b %Y %H:%M:%S GMT')

            return formatted_time
        else:
            return obj