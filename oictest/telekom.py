#!/usr/bin/env python
import json

__author__ = 'rolandh'


BASE = "https://accounts.login00.idm.ver.sul.t-online.de"

from default import DEFAULT

info = DEFAULT.copy()

info["provider"] = {
    "authorization_endpoint": "%s/oic" % BASE,
    "token_endpoint": "%s/oauth2/tokens" % BASE,
    "userinfo_endpoint": "%s/userinfo" % BASE,
    "response_types_supported": ["code"],
    "scopes_supported": ["openid", "profile"],
    "token_endpoint_auth_methods_supported": ["client_secret_basic"]
}

info["interaction"] = [
    {
        "matches": {
            "url": "%s/oic" % BASE
        },
        "page-type": "login",
        "control": {
            "type": "form",
            "set": {"pw_usr": "openidtest",
                    "pw_pwd": "test3452"}
        }
    },

]

info["features"]["registration"] = False
info["features"]["discovery"] = False

info["client"]["client_id"] = "10TVL0SAM30000004901OIC10000000000000000"
info["client"]["client_secret"] = "46795C66-6DE3-F26C-7951-678E072AB3CA"

print json.dumps(info)