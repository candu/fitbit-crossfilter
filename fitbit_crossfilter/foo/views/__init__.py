from xhpy.pylib import *

from django.http import HttpResponse

from foo.ui.list import :ui:list
from foo.lib.fitbit import Fitbit

def index(request):
    page = \
    <ui:list items={range(3)} />
    fitbit = Fitbit()
    # TODO: do something with this!
    return HttpResponse(page)
