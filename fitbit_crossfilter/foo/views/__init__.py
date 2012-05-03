from xhpy.pylib import *

import datetime
import json
import oauth2
import time
import urlparse

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect

from foo.models import UserData
from foo.ui.page import :ui:page
from foo.lib.fitbit import Fitbit

MS_PER_S = 1000
S_PER_MIN = 60

def index(request):
    if request.session.get('access_token') is None:
        return redirect('/login')
    access_token = oauth2.Token.from_string(request.session['access_token'])
    page = \
    <ui:page>
        <div id="header">
            <h1 id="banner">Fitbit + Crossfilter</h1>
        </div>
        <div id="body">
        <p>
        This dashboard uses the
        <a href="http://dev.fitbit.com/">Fitbit API</a>
        with
        <a href="http://http://square.github.com/crossfilter/">Crossfilter</a>
        to display your Fitbit data over the last 60 days.
        </p>
        <p id="links">
            <a href="javascript:resetAll()">reset all</a>
        </p>
        <div id="charts">
            <div id="date-chart" class="chart">
                <div class="title">Date</div>
            </div>
            <div id="hour-chart" class="chart">
                <div class="title">Time of Day</div>
            </div>
            <div id="steps-chart" class="chart">
                <div class="title">steps / min</div>
            </div>
            <div id="calories-chart" class="chart">
                <div class="title">kcal / min</div>
            </div>
            <div id="floors-chart" class="chart">
                <div class="title">floors / min</div>
            </div>
            <div id="activescore-chart" class="chart">
                <div class="title">Active Score (x1000)</div>
            </div>
            <div id="awakeningscount-chart" class="chart">
                <div class="title">Times Awoken</div>
            </div>
            <div id="minutestofallasleep-chart" class="chart">
                <div class="title">Time to Asleep (min)</div>
            </div>
            <div id="timeinbed-chart" class="chart">
                <div class="title">Sleep (h)</div>
            </div>
        </div>
        </div>
        <div id="footer">
            Page loading...
        </div>
    </ui:page>
    return HttpResponse(unicode(page))

def get_user_data(request):
    if request.session.get('access_token') is None:
        return redirect('/login')
    access_token = oauth2.Token.from_string(request.session['access_token'])
    user_id = request.session['user_id']
    two_months_ago = datetime.date.today() - datetime.timedelta(days=60)
    query = UserData.objects.filter(
            user_id=user_id, date__gte=two_months_ago)
    data = list(json.loads(row.data) for row in query)
    return HttpResponse(json.dumps(data),
                        content_type='application/json')

def _get_time_series_for_user_data(data):
    def date_to_js_timestamp(date):
        d = datetime.datetime.strptime(date, '%Y-%m-%d')
        return int(MS_PER_S * time.mktime(d.timetuple()))
    date = data['activeScore']['activities-activeScore'][0]['dateTime']
    timestamp = date_to_js_timestamp(date)
    # daily activity metrics
    activeScore = int(data['activeScore']['activities-activeScore'][0]['value'])
    # daily sleep metrics
    awakeningsCount = int(data['awakeningsCount']['sleep-awakeningsCount'][0]['value'])
    minutesToFallAsleep = int(data['minutesToFallAsleep']['sleep-minutesToFallAsleep'][0]['value'])
    timeInBed = int(data['timeInBed']['sleep-timeInBed'][0]['value'])
    # daily direct data
    totalCalories = int(data['calories']['activities-log-calories'][0]['value'])
    totalFloors = int(data['floors']['activities-log-floors'][0]['value'])
    totalSteps = int(data['steps']['activities-log-steps'][0]['value'])
    summary = {
        'activeScore': activeScore,
        'awakeningsCount': awakeningsCount,
        'minutesToFallAsleep': minutesToFallAsleep,
        'timeInBed': timeInBed,
        'totalCalories': totalCalories,
        'totalFloors': totalFloors,
        'totalSteps': totalSteps
        }
    ts_columns = [
        'timestamp',
        'steps',
        'calories',
        'floors',
    ]
    ts = []
    for i in xrange(1440):
        steps = int(data['steps']['activities-log-steps-intraday']['dataset'][i]['value'])
        if steps > 0:
            calories = float(data['calories']['activities-log-calories-intraday']['dataset'][i]['value'])
            floors = int(data['floors']['activities-log-floors-intraday']['dataset'][i]['value'])
            ts.append([
                timestamp,
                steps,
                calories,
                floors,
            ])
        timestamp += MS_PER_S * S_PER_MIN
    return {
        'summary': summary,
        'ts_columns': ts_columns,
        'ts': ts,
    }

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
    end_date = Fitbit.get_user_last_sync_date(access_token)
    while next_date < end_date:
        data = Fitbit.get_user_data_by_date(access_token, next_date)
        time_series = _get_time_series_for_user_data(data)
        user_data = UserData(user_id=user_id,
                             date=next_date,
                             data=json.dumps(time_series))
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
