from xhpy.pylib import *

from django.http import HttpResponse

from foo.ui.list import :ui:list
from foo.lib.fitbit import Fitbit

def index(request):
    fitbit = Fitbit()
    url = '/1/user/-/activities/steps/date/today/7d.json'
    data = fitbit.request(url)
    page = \
    <ui:list items={[data]} />
    return HttpResponse(page)
