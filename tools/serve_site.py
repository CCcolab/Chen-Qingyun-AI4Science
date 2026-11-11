#!/usr/bin/env python3
"""Serve the same immutable site at / and a repository prefix on loopback."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]


def normalize_prefix(value):
    parts = value.strip('/').split('/')
    if not all(p and p not in ('.', '..') and all(c.isalnum() or c in '-_.' for c in p) for p in parts):
        raise ValueError('Prefix must contain plain path components')
    return '/' + '/'.join(parts) + '/'


class SiteHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory, prefix, **kwargs):
        self.prefix = normalize_prefix(prefix)
        super().__init__(*args, directory=str(directory), **kwargs)

    def translate_path(self, path):
        parsed = urlsplit(path)
        request_path = parsed.path
        if request_path.startswith(self.prefix):
            request_path = '/' + request_path[len(self.prefix):]
        return super().translate_path(urlunsplit(('', '', request_path, parsed.query, '')))

    def log_message(self, *args):
        pass


def create_server(port=0, prefix='/Chen-Qingyun-AI4Science/'):
    handler = partial(SiteHandler, directory=ROOT / 'site', prefix=prefix)
    return ThreadingHTTPServer(('127.0.0.1', port), handler)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--prefix', default='/Chen-Qingyun-AI4Science/')
    args = parser.parse_args()
    with create_server(args.port, args.prefix) as server:
        print(f'Root: http://127.0.0.1:{server.server_port}/', flush=True)
        print(f'Project: http://127.0.0.1:{server.server_port}{normalize_prefix(args.prefix)}', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
