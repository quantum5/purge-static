from __future__ import print_function

import argparse
import os
import re
import shelve
import sys
from contextlib import closing
from hashlib import sha256
from textwrap import dedent

from purge_static.cdn import *


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=dedent('''\
            Find changed static files, show their URLs, and optionally purge them
            for you on your CDN.

            This tool can be used to enable aggressive caching for your static site.
            You can cache your entire static site on CDN edge nodes, and then use this
            tool to purge all static files that changed on disk, by file hash (SHA256).
            
            Currently, only CloudFlare is supported.
        '''))

    parser.add_argument('url', help='URL prefix corresponding to --dir')

    parser.add_argument('-d', '--dir', default='.',
                        help='local filesystem path corresponding to --url')
    parser.add_argument('-S', '--select',
                        help='regex to run on file names to select files to be purged, '
                             'matched from the start of the string')
    parser.add_argument('-i', '--ignore',
                        help='regex to run on file names to ignore files, '
                             'matched from the start of the string')
    parser.add_argument('-I', '--index', action='append',
                        help='file to consider as directory index (repeatable, default: index.html)')
    parser.add_argument('-s', '--store',
                        help='file to store hashes in (default: $dir/.purge-static)')
    parser.add_argument('-D', '--dry-run', action='store_true', help="dry run, don't update hashes")
    parser.add_argument('-q', '--quiet', help='reduce output')

    cdn_group = parser.add_argument_group(title='CDN options')
    cdn_group.add_argument('--cloudflare', dest='cdn', action='store_const', const=CloudFlareCDN,
                           help='purge files on CloudFlare CDN. need --credentials, which must be '
                                'a JSON files with two keys, email and api_key, containing your '
                                'CloudFlare account email and API key. need --zone, which must '
                                'be your CloudFlare zone ID (the hex code)')
    cdn_group.add_argument('-c', '--credentials', help='credentials file path')
    cdn_group.add_argument('-z', '--zone', help='zone ID (for CloudFlare)')

    args = parser.parse_args()

    if args.cdn:
        cdn = args.cdn(args)
    else:
        cdn = None

    def select_regex(name):
        regex = getattr(args, name)
        if regex:
            try:
                return re.compile(regex)
            except re.error:
                sys.exit('Invalid regex for %s: %s' % (name, regex))

    select = select_regex('select')
    ignore = select_regex('ignore')
    indexes = args.index or ['index.html']
    store = args.store or os.path.join(args.dir, '.purge-static')

    url_prefix = args.url
    if not url_prefix.endswith('/'):
        url_prefix += '/'

    urls = []
    with closing(shelve.open(store, protocol=2)) as store:
        for dirpath, _, filenames in os.walk(args.dir):
            relpath = os.path.relpath(dirpath, args.dir)

            urlpath = relpath.replace(os.sep, '/')
            if os.altsep:
                urlpath = urlpath.replace(os.altsep, '/')
            if urlpath == os.curdir:
                urlpath = ''
            else:
                urlpath += '/'

            changed = set()
            for filename in filenames:
                if select and not select.match(filename):
                    continue
                if ignore and ignore.match(filename):
                    continue

                path = os.path.join(dirpath, filename)
                hasher = sha256()
                with open(os.path.join(args.dir, path), 'rb') as f:
                    for block in iter(lambda: f.read(65536), b''):
                        hasher.update(block)

                if hasher.digest() != store.get(path):
                    if not args.dry_run:
                        store[path] = hasher.digest()
                    urls.append(url_prefix + urlpath + filename)
                    changed.add(filename)

            for index in indexes:
                if index in filenames:
                    if index in changed:
                        urls.append(url_prefix + urlpath)
                    break

    if cdn:
        if urls:
            cdn.purge(urls)
            if not args.quiet:
                print('Success: %d URLs purged' % len(urls))
        elif not args.quiet:
            print('Nothing to change')
    else:
        for path in urls:
            print(path)
