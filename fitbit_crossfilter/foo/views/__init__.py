from xhpy.pylib import *

from django.http import HttpResponse

from foo.ui.list import :ui:list

def index(request):
    page = \
    <ui:list items={range(3)} />
    return HttpResponse(page)
