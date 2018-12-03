import json
import sys

import requests
import six


class CloudFlareCDN(object):
    def __init__(self, args):
        if not args.credentials:
            sys.exit('No credentials for CloudFlare, use --credentials.')

        try:
            with open(args.credentials) as f:
                credentials = json.load(f)
        except IOError:
            sys.exit('Cannot read credentials file: %s' % (args.credentials,))
        except ValueError:
            sys.exit('Credentials file not valid JSON: %s' % (args.credentials,))

        self.email = credentials.get('email')
        if not isinstance(self.email, six.string_types):
            sys.exit('In credentials file: key "email" should map to a string')

        self.api_key = credentials.get('api_key')
        if not isinstance(self.api_key, six.string_types):
            sys.exit('In credentials file: key "api_key" should map to a string')

        self.zone = args.zone
        if not self.zone:
            sys.exit('No zone for CloudFlare, use --zone.')

    def purge(self, urls):
        resp = requests.post(
            'https://api.cloudflare.com/client/v4/zones/%s/purge_cache' % (self.zone,),
            json={'files': urls}, headers={
                'X-Auth-Email': self.email,
                'X-Auth-Key': self.api_key,
            }
        ).json()

        if resp.get('success'):
            return

        sys.exit(resp)
