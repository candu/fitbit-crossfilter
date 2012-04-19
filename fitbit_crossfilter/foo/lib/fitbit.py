import BaseHTTPServer
import oauth2
import json
import webbrowser
import urlparse
from ...settings import *

AUTH_HOST = 'www.fitbit.com'
API_HOST = 'api.fitbit.com'

AUTH_URL = 'http://{0}/oauth/authorize'.format(AUTH_HOST)
REQUEST_TOKEN_URL = 'http://{0}/oauth/request_token'.format(API_HOST)
ACCESS_TOKEN_URL = 'http://{0}/oauth/access_token'.format(API_HOST)
SERVER_PORT = 9001

OAUTH_DATA = None
OAUTH_DATA_FILE = '.fitbit_access_token'

AUTH_SUCCESS_HTML = """
fitbit login succeeded! you can close this window now.
"""

AUTH_FAILURE_HTML = """
fitbit login failed! oh no!
"""

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        global OAUTH_DATA
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        query = urlparse.urlparse(self.path).query
        params = urlparse.parse_qs(query)
        oauth_token = params.get('oauth_token', [None])[0]
        if oauth_token is None:
            self.wfile.write(AUTH_FAILURE_HTML)
        else:
            OAUTH_DATA = dict((k, v[0]) for k, v in params.iteritems())
            open(OAUTH_DATA_FILE, 'w').write(json.dumps(OAUTH_DATA))
            self.wfile.write(AUTH_SUCCESS_HTML)

def main():
    global OAUTH_DATA

    consumer_key = FITBIT_CONSUMER_KEY
    consumer_secret = FITBIT_CONSUMER_SECRET

    consumer = oauth2.Consumer(key=consumer_key, secret=consumer_secret)
    client = oauth2.Client(consumer)

    # Get request token
    resp, content = client.request(REQUEST_TOKEN_URL, 'GET')
    status = resp['status']
    if status != '200':
        raise Exception('HTTP {error_code}'.format(error_code=status))
    request_token = dict(urlparse.parse_qsl(content))
    token = oauth2.Token(key=request_token['oauth_token'],
                         secret=request_token['oauth_token_secret'])

    # Ask user to authenticate this token
    print "Request Token:"
    print "    - oauth_token        = %s" % token.key
    print "    - oauth_token_secret = %s" % token.secret
    print

    webbrowser.open('{0}?oauth_token={1}'.format(AUTH_URL, token.key))
    httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', SERVER_PORT),
                                      RequestHandler)
    while OAUTH_DATA is None:
        httpd.handle_request()

    # Request access token approved by user
    token.set_verifier(OAUTH_DATA['oauth_verifier'])
    client = oauth2.Client(consumer, token)
    resp, content = client.request(ACCESS_TOKEN_URL, 'POST')
    access_token = dict(urlparse.parse_qsl(content))

    print "Access Token:"
    print "    - oauth_token        = %s" % access_token['oauth_token']
    print "    - oauth_token_secret = %s" % access_token['oauth_token_secret']
    print
    print "You may now access protected resources using the access tokens above."
    print

if __name__ == '__main__':
    main()
