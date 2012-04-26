import httplib
import json
import oauth2
import urllib

from django.conf import settings

class Fitbit(object):
    AUTH_HOST = 'www.fitbit.com'
    API_HOST = 'api.fitbit.com'

    AUTH_URL = 'http://{0}/oauth/authorize'.format(AUTH_HOST)
    REQUEST_TOKEN_URL = 'http://{0}/oauth/request_token'.format(API_HOST)
    ACCESS_TOKEN_URL = 'http://{0}/oauth/access_token'.format(API_HOST)

    SIGNATURE_METHOD = oauth2.SignatureMethod_PLAINTEXT()

    CONSUMER = oauth2.Consumer(key=settings.FITBIT_CONSUMER_KEY,
                               secret=settings.FITBIT_CONSUMER_SECRET)

    @classmethod
    def get_token(cls):
        client = oauth2.Client(cls.CONSUMER)
        resp, content = client.request(cls.REQUEST_TOKEN_URL, 'GET')
        status = resp['status']
        if status != '200':
            raise Exception('HTTP {error_code}'.format(error_code=status))
        print 'Request Token: {0}'.format(content)
        return oauth2.Token.from_string(content)

    @classmethod
    def get_auth_url(cls, token):
        params = {'oauth_token': token.key}
        return '{0}?{1}'.format(cls.AUTH_URL, urllib.urlencode(params))

    @classmethod
    def get_access_token(cls, token, oauth_verifier):
        token.set_verifier(oauth_verifier)
        client = oauth2.Client(cls.CONSUMER, token)
        resp, content = client.request(cls.ACCESS_TOKEN_URL, 'POST')
        status = resp['status']
        if status != '200':
            raise Exception('HTTP {error_code}'.format(error_code=status))
        print 'Access Token: {0}'.format(content)
        return oauth2.Token.from_string(content)

    @classmethod
    def get_current_user_id(cls, access_token):
        url = '/1/user/-/profile.json'
        data = json.loads(cls.request(access_token, url))
        return data['user']['encodedId']

    @classmethod
    def request(cls, access_token, url):
        consumer = cls.CONSUMER
        full_url = 'http://{0}{1}'.format(cls.API_HOST, url)
        oauth_request = oauth2.Request.from_consumer_and_token(
                cls.CONSUMER,
                token=access_token,
                http_url=full_url)
        oauth_request.sign_request(
                cls.SIGNATURE_METHOD,
                cls.CONSUMER,
                access_token)
        headers = oauth_request.to_header(realm=cls.API_HOST)
        # TODO: handle HTTP errors here...
        connection = httplib.HTTPSConnection(cls.API_HOST)
        connection.request('GET', full_url, headers=headers)
        resp = connection.getresponse()
        data = resp.read()
        return data
