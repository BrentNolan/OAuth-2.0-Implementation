#!/usr/bin/env python

import os
import webapp2
import json
import string
import random
import urllib2
import urllib
from google.appengine.ext.webapp import template


# Secret generation function from
# http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python


def state_gen(size=30, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


# [START Handlers]


class SignIn(webapp2.RequestHandler):

    def get(self, id=None):
        url = 'https://accounts.google.com/o/oauth2/v2/auth'
        stateg = state_gen()
        values = {'response_type': 'code',
                  'client_id': '238284068035-o7o6g5soe65cuqkfqcahlij5d4hu65or.apps.googleusercontent.com',
                  'redirect_uri': 'https://oauth2-nolanbr.appspot.com/oauth',
                  'scope': 'email',
                  'state': stateg,
                  'access_type': 'offline'
                  }
        data = urllib.urlencode(values)
        address = url + '?' + data
        print address
        self.redirect(address)

class OAuth(webapp2.RequestHandler):

    def get(self, id=None):
        state = self.request.get("state")
        authcode = self.request.get("code")

        url = "https://www.googleapis.com/oauth2/v4/token/"
        data_to_post = {
            'code': authcode,
            'client_id': '238284068035-o7o6g5soe65cuqkfqcahlij5d4hu65or.apps.googleusercontent.com',
            'client_secret': 'VYJn-UiST3wLYxrYHlimCcRT',
            'redirect_uri': 'https://oauth2-nolanbr.appspot.com/oauth',
            'grant_type': 'authorization_code'
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        encoded_data = urllib.urlencode(data_to_post)
        req = urllib2.Request(url, encoded_data, headers)
        json_result = json.loads(urllib2.urlopen(req).read())
        authorizeString = 'Bearer ' + json_result['access_token']
        req2 = urllib2.Request('https://www.googleapis.com/plus/v1/people/me')
        req2.add_header('Authorization', authorizeString)
        json_resp = json.loads(urllib2.urlopen(req2).read())
        if 'url' in json_resp:
            userurl = json_resp['url']
        else:
            userurl = 'No Google+ URL for this account'
        if 'displayName' in json_resp:
            username = json_resp['displayName']
        else:
            username = 'No Google displayName for this account'

        template_values = {
            'userName': username,
            'userURL': userurl,
            'state': state

        }
        path = os.path.join(os.path.dirname(__file__), 'oauth.html')
        self.response.out.write(template.render(path, template_values))


# [END Handlers]

# [START main_page]
class MainPage(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))
# [END main_page]

allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/signin', SignIn),
    ('/oauth', OAuth)

], debug=True)
# [END app]
