import BaseHTTPServer
import oauth2
import json
import webbrowser
import urlparse
import httplib
from django.conf import settings

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

class _RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
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

class Fitbit(object):
    def __init__(self,
                 consumer_key = settings.FITBIT_CONSUMER_KEY,
                 consumer_secret = settings.FITBIT_CONSUMER_SECRET):
        consumer = oauth2.Consumer(key=consumer_key,
                                         secret=consumer_secret)
        client = oauth2.Client(consumer)

        # Get request token
        resp, content = client.request(REQUEST_TOKEN_URL, 'GET')
        status = resp['status']
        if status != '200':
            raise Exception('HTTP {error_code}'.format(error_code=status))
        token = oauth2.Token.from_string(content)
        print 'Request Token: {0}'.format(token)

        # Ask user to authenticate this token
        webbrowser.open('{0}?oauth_token={1}'.format(AUTH_URL, token.key))
        httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', SERVER_PORT),
                                          _RequestHandler)
        while OAUTH_DATA is None:
            httpd.handle_request()

        # Request access token approved by user
        token.set_verifier(OAUTH_DATA['oauth_verifier'])
        client = oauth2.Client(consumer, token)
        resp, content = client.request(ACCESS_TOKEN_URL, 'POST')
        access_token = oauth2.Token.from_string(content)
        print 'Access Token: {0}'.format(access_token)

        self._consumer = consumer
        self._token = token
        self._access_token = access_token
        self._signature_method = oauth2.SignatureMethod_PLAINTEXT()

    def request(self, url):
        full_url = 'http://{0}{1}'.format(API_HOST, url)
        oauth_request = oauth2.Request.from_consumer_and_token(
                self._consumer,
                token=self._access_token,
                http_url=full_url)
        oauth_request.sign_request(
                self._signature_method,
                self._consumer,
                self._access_token)
        headers = oauth_request.to_header(realm=API_HOST)
        connection = httplib.HTTPSConnection(API_HOST)
        connection.request('GET', full_url, headers=headers)
        resp = connection.getresponse()
        data = resp.read()
        return data
