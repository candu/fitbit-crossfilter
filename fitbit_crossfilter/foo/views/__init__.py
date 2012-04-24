from xhpy.pylib import *

import json
import oauth2
import urllib
import urlparse

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect

from foo.ui.page import :ui:page
from foo.lib.fitbit import Fitbit

# TODO: put these in settings

def index(request):
    if request.session.get('access_token') is None:
        return redirect('/login')
    # url = '/1/user/-/activities/steps/date/today/7d.json'
    url = '/1/user/-/activities/log/steps/date/2012-04-22/1d.json'
    access_token = oauth2.Token.from_string(request.session['access_token'])
    data = json.loads(Fitbit.request(access_token, url))
    page = \
    <ui:page>
        {json.dumps(data)}
    </ui:page>
    return HttpResponse(page)

def login(request):
    if request.session.get('access_token') is not None:
        return redirect('/')
    client = oauth2.Client(Fitbit.CONSUMER)
    resp, content = client.request(Fitbit.REQUEST_TOKEN_URL, 'GET')
    status = resp['status']
    if status != '200':
        raise Exception('HTTP {error_code}'.format(error_code=status))
    token = oauth2.Token.from_string(content)
    request.session['token'] = token.to_string()
    print 'Request Token: {0}'.format(token)
    params = {
        'oauth_token': token.key,
    }
    url = '{0}?{1}'.format(Fitbit.AUTH_URL, urllib.urlencode(params))
    return redirect(url)

def logout(request):
    if request.session.get('access_token') is not None:
        del request.session['token']
        del request.session['access_token']
    return redirect('/login')

def oauth(request):
    if request.session.get('token') is None:
        return redirect('/')
    oauth_token = request.GET.get('oauth_token')
    if oauth_token is None:
        raise Exception('no oauth_token in callback request params!')
    token = oauth2.Token.from_string(request.session['token'])
    token.set_verifier(request.GET['oauth_verifier'])

    client = oauth2.Client(Fitbit.CONSUMER, token)
    resp, content = client.request(Fitbit.ACCESS_TOKEN_URL, 'POST')
    status = resp['status']
    if status != '200':
        raise Exception('HTTP {error_code}'.format(error_code=status))
    print 'Access Token: {0}'.format(content)
    request.session['access_token'] = content
    # TODO: actually get userid via API here
    # url = 'whatever'
    # fitbit = Fitbit.request(url)
    return redirect('/')
