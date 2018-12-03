# `purge-static` [![PyPI](https://img.shields.io/pypi/v/purge-static.svg)](https://pypi.org/project/purge-static/) [![PyPI - Format](https://img.shields.io/pypi/format/purge-static.svg)](https://pypi.org/project/purge-static/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/purge-static.svg)](https://pypi.org/project/purge-static/)

`purge-static` is a tool to find changed static files, show their URLs,
and optionally purge them for you on your CDN, such as CloudFlare.

With `purge-static`, you can enable aggressive caching for your static
site on your CDN, caching the entire site on the CDN edge. When you update
your site, you simply need to use `purge-static` to purge only the changed
files.

`purge-static` uses the SHA256 hash of files to determine if they changed.

## Installation

```
pip install purge-static
```

## Example Invocation

```sh
purge-static -d /path/to/my/webroot -u https://example.com
```

If your webroot is not writable, you can select a different path to write
the hash store with `--store /path/to/a/file/to/store/hashes`.

This example ignores all `.gz` files, since they are only used for `nginx`'s
`gzip_static` module, as well as all files with hash already in the name:

```sh
purge-static -d /path/to/my/webroot -u https://example.com \
    -i '.*\.gz$|.*-[0-9a-f]{64}\.'
```

For more detailed description of the arguments, run `purge-static --help`.

## CloudFlare

To use CloudFlare, you will need to create a credentials file:

```json
{
    "email": "you@example.com",
    "api_key": "myverysecretapikey"
}
```

Then, you can invoke `purge-static`:

```sh
purge-static -d /path/to/my/webroot -u https://example.com \
    --cloudflare -c /path/to/my/credentiails -z mycloudflarezoneid
```

Note that `-z` takes the CloudFlare zone ID as 32 hex digits.
