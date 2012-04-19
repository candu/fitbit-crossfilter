from xhpy.pylib import *

class :ui:list(:x:element):
    attribute list items
    def render(self):
        list_elem = <ul />
        for item in self.getAttribute('items'):
            list_elem.appendChild(<li>{item}</li>)
        return list_elem
