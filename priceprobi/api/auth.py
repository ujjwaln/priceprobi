__author__ = 'ujjwal'

import json
import uuid

from eve.auth import BasicAuth
from flask import current_app as app

from priceprobi.utils import get_json
from priceprobi.utils import get_magic_user


def check_fb_access_token(fbId, accessToken):
    url = 'https://graph.facebook.com/me?access_token=%s' % accessToken
    str_response = get_json(url, None, None)
    if str_response:
        obj = json.loads(str_response)
        if fbId == obj["id"]:
            return True

    return False


def get_pp_user(fb_id, access_token, allowed_roles=None):
    #check if fbId, accessToken is present in accounts
    users = app.data.driver.db['user']
    user = users.find_one({'fbId': fb_id})

    #fbId, accessToken combo is present
    if user and user['accessToken'] == access_token:
        return {
            "status": ['OK'],
            "user": user
        }

    #fbId is present, accessToken needs to be updated
    elif user and user['accessToken'] != access_token:
        #check if supplied accessToken is valid
        fb_check = app.settings['ENABLE_FB_ACCESS_TOKEN_CHECK']
        if fb_check:
            fb_check_val = check_fb_access_token(fb_id, access_token)
            if not fb_check_val:
                return {
                    "status": ['USER_ALREADY_REGISTERED', 'INVALID_FB_ACCESS_TOKEN'],
                    "user": None
                }

        appToken = str(uuid.uuid4())
        user['accessToken'] = access_token
        user['appToken'] = appToken
        users.update({'_id': user['_id']}, user)
        return {
            "status": ['OK', 'UPDATED_FB_ACCESS_TOKEN'],
            "user": user
        }

    #this is a new fbId so insert into account
    elif user is None:
        fb_check_val = check_fb_access_token(fb_id, access_token)
        if fb_check_val:
            appToken = str(uuid.uuid4())
            if allowed_roles is None:
                allowed_roles = ['user']
            userData = {
                'fbId': fb_id,
                'accessToken': access_token,
                'cfToken': appToken,
                'expires': 0,
                'roles': allowed_roles
            }
            user_id = users.insert(userData)
            inserted_user = users.find_one({'_id': user_id})
            return {
                "status": ['USER_CREATED'],
                "user": inserted_user
            }
        else:
            #Invalid Request, do not issue token
            return {
                "status": ['ERR'],
                "user": None
            }


class PPApiBasicAuth(BasicAuth):
    def check_auth(self, fb_id, cf_token, allowed_roles, resource, method):
        users = app.data.driver.db['user']
        user = users.find_one({'fbId': fb_id})
        if user and (user['cfToken'] == cf_token):
            return True

        return False


class PPApiBasicAuth_Test(BasicAuth):
    def check_auth(self, fb_id, cf_token, allowed_roles, resource, method):
        magic_user = get_magic_user()
        if fb_id == magic_user["fbId"] and cf_token == magic_user["cfToken"]:
            return True

        return False
