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
            <link href='http://fonts.googleapis.com/css?family=Oxygen' rel='stylesheet' type='text/css' />
            <ui:css path="base.css" />
            <ui:js path="crossfilter.js" />
            <ui:js path="d3.js" />
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
                    <ui:js path="base.js" />
                </body>
            </html>
        </x:doctype>
