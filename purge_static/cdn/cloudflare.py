import json
import sys

import requests

from purge_static.utils import chunk

CLOUDFLARE_MAX_PURGE = 30


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

        self.api_token = credentials.get('api_token')
        if self.api_token:
            if not isinstance(self.api_token, str):
                sys.exit('In credentials file: key "api_token" should map to a string')

            self.email = self.api_key = None
        else:
            self.email = credentials.get('email')
            if not isinstance(self.email, str):
                sys.exit('In credentials file: key "email" should map to a string')

            self.api_key = credentials.get('api_key')
            if not isinstance(self.api_key, str):
                sys.exit('In credentials file: key "api_key" should map to a string')

        self.zone = args.zone
        if not self.zone:
            sys.exit('No zone for CloudFlare, use --zone.')

    def purge(self, urls):
        if self.api_token:
            headers = {'Authorization': f'Bearer {self.api_token}'}
        else:
            headers = {
                'X-Auth-Email': self.email,
                'X-Auth-Key': self.api_key,
            }

        for group in chunk(urls, CLOUDFLARE_MAX_PURGE):
            resp = requests.post(
                'https://api.cloudflare.com/client/v4/zones/%s/purge_cache' % (self.zone,),
                json={'files': group}, headers=headers
            ).json()

            if not resp.get('success'):
                sys.exit(resp)
