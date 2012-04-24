from xhpy.pylib import *
from foo.ui.css import :ui:css
from foo.ui.js import :ui:js

class :ui:page(:x:element):
    attribute string title
    def render(self):
        title = self.getAttribute('title')
        head = \
        <head>
            <title>{title}</title>
            <ui:css path="base.css" />
            <ui:js path="crossfilter.js" />
            <ui:js path="d3.js" />
            <ui:js path="base.js" />
        </head>
        container = <div id="container" />
        for child in self.getChildren():
            container.appendChild(child)
        return \
        <x:doctype>
            <html>
                {head}
                <body>
                    {container}
                </body>
            </html>
        </x:doctype>
