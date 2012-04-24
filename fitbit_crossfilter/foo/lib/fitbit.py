import httplib
import oauth2

from django.conf import settings

# TODO: put in settings
API_HOST = 'api.fitbit.com'

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
    def request(cls, access_token, url):
        consumer = cls.CONSUMER
        full_url = 'http://{0}{1}'.format(API_HOST, url)
        oauth_request = oauth2.Request.from_consumer_and_token(
                cls.CONSUMER,
                token=access_token,
                http_url=full_url)
        oauth_request.sign_request(
                cls.SIGNATURE_METHOD,
                cls.CONSUMER,
                access_token)
        headers = oauth_request.to_header(realm=API_HOST)
        # TODO: handle HTTP errors here...
        connection = httplib.HTTPSConnection(API_HOST)
        connection.request('GET', full_url, headers=headers)
        resp = connection.getresponse()
        data = resp.read()
        return data
