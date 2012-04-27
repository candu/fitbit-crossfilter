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
    page = \
    <ui:page>
        {json.dumps(data)}
    </ui:page>
    return HttpResponse(page)

def get_user_data(request):
    if request.session.get('access_token') is None:
        return redirect('/login')
    access_token = oauth2.Token.from_string(request.session['access_token'])
    user_id = request.session['user_id']
    one_month_ago = datetime.date.today() - datetime.timedelta(days=30)
    query = UserData.objects.filter(user_id=user_id, date__gte=one_month_ago)
    data = {}
    for row in query:
        date = row.date.strftime('%Y-%m-%d')
        data[date] = row.data
    return HttpResponse(json.dumps(data),
                        content_type='application/json')

def sync_user_data(request):
    if request.session.get('access_token') is None:
        return redirect('/login')
    access_token = oauth2.Token.from_string(request.session['access_token'])
    user_id = request.session['user_id']
    dates = list(UserData.objects.filter(user_id=user_id).values('date'))
    dates = sorted(map(lambda d: d['date'], dates))
    if dates:
        next_date = dates[-1] + datetime.timedelta(days=1)
    else:
        next_date = Fitbit.get_user_joined_date(access_token)
        next_date = datetime.datetime.strptime(next_date, '%Y-%m-%d').date()
    end_date = datetime.date.today()
    while next_date < end_date:
        print 'loading date {0}'.format(next_date)
        data = Fitbit.get_user_data_by_date(access_token, next_date)
        user_data = UserData(user_id=user_id,
                             date=next_date,
                             data=data)
        user_data.save()
        next_date += datetime.timedelta(days=1)
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
