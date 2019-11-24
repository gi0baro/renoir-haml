# -*- coding: utf-8 -*-
"""
    renoir_haml.ext
    ---------------

    Provides the Haml extension for Renoir

    :copyright: (c) 2017-2019 by Giovanni Barillari
    :license: BSD, see LICENSE for more details.
"""

import os

from renoir.extensions import Extension

from .hamlpy import Compiler


class Haml(Extension):
    file_extension = 'haml'
    default_config = dict(
        encoding='utf8',
        reload=False
    )

    def on_load(self):
        self.config['reload'] = self.config['reload'] or self.templater.debug
        self.get_template = (
            self._reloader_get if self.config['reload'] else self._cached_get)
        self.env.mtimes = {}
        self.env.builds = {}
        self.compiler = Compiler()

    @staticmethod
    def _read_source(file_path, encoding='utf8'):
        with open(file_path, 'r', encoding=encoding) as source_file:
            rv = source_file.read()
        return rv

    @staticmethod
    def _store_compiled(file_path, data, encoding='utf8'):
        with open(f'{file_path}.html', 'w', encoding=encoding) as dest_file:
            dest_file.write(data)

    def _build_html(self, file_path, file_name):
        source = self._read_source(file_path)
        haml = self.compiler.process_lines(source.splitlines())
        self._store_compiled(file_path, haml)
        self.env.mtimes[file_path] = os.stat(file_path).st_mtime
        self.env.builts[file_path] = f'{file_name}.html'
        return self.env.builts[file_path]

    def _is_cache_valid(self, file_path):
        try:
            mtime = os.stat(file_path).st_mtime
        except Exception:
            return False
        old_time = self.env.mtimes.get(file_path, 0)
        if mtime > old_time:
            return False
        return True

    def _reloader_get(self, file_path):
        if self._is_cache_valid(file_path):
            return self._cached_get(file_path)
        return None

    def _cached_get(self, file_path):
        return self.env.builts.get(file_path)

    def load(self, path, file_name):
        file_path = os.path.join(path, file_name)
        html_name = self.get_template(file_path) or self._build_html(
            file_path, file_name)
        return path, html_name
