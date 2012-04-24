from xhpy.pylib import *

from django.conf import settings

class :ui:css(:x:element):
    attribute string path
    def render(self):
        path = self.getAttribute('path')
        return <link href={settings.STATIC_URL + path} rel="stylesheet" type="text/css" />
