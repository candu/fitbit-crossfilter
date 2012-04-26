from xhpy.pylib import *

import datetime
import json
import oauth2
import urlparse

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect

from foo.models import UserData
from foo.ui.page import :ui:page
from foo.lib.fitbit import Fitbit

def index(request):
    if request.session.get('access_token') is None:
        return redirect('/login')
    url = '/1/user/-/activities/log/steps/date/2012-04-22/1d.json'
    access_token = oauth2.Token.from_string(request.session['access_token'])
    data = Fitbit.get_user_data_by_date(
            access_token, datetime.date(year=2012, month=4, day=22))
    page = \
    <ui:page>
        {json.dumps(data)}
    </ui:page>
    return HttpResponse(page)

def get_user_data(request):
    if request.session.get('access_token') is None:
        return redirect('/login')
    """
    if user_has_no_data():
        time_series = fetch_time_series_max()
        start_date = time_series[0]
    else:
        start_date = first_day_where_user_has_no_data()
    end_date = today()
    if start_date == end_date:
        # TODO: return some success status
        return HttpResponse(json.dumps({'status': 'ok'}),
                        content_type='application/json')
    fetch_time_series(start_date, end_date)
    for date in range(start_date, end_date):
        fetch_intraday_data(date)
    """
    return HttpResponse(json.dumps({'status': 'ok'}),
                        content_type='application/json')

def login(request):
    if request.session.get('access_token') is not None:
        return redirect('/')
    token = Fitbit.get_token()
    request.session['token'] = token.to_string()
    return redirect(Fitbit.get_auth_url(token))

def logout(request):
    if request.session.get('access_token') is not None:
        del request.session['token']
        del request.session['access_token']
    return redirect('/login')

def oauth(request):
    if request.session.get('token') is None:
        return redirect('/')
    oauth_verifier = request.GET.get('oauth_verifier')
    if oauth_verifier is None:
        raise Exception('no oauth_verifier in callback request params!')
    token = oauth2.Token.from_string(request.session['token'])
    access_token = Fitbit.get_access_token(token, oauth_verifier)
    request.session['access_token'] = access_token.to_string()
    request.session['user_id'] = Fitbit.get_current_user_id(access_token)
    return redirect('/')
