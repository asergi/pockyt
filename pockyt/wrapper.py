from __future__ import absolute_import, print_function, unicode_literals, with_statement

import os
import sys
import traceback
import webbrowser
from collections import OrderedDict

import requests

from .api import API


def print_bug_report(message=''):
    """
    Prints a usable bug report
    """

    separator = '\n' + ('-' * 69) + '\n'

    python_version = str(sys.version_info[:3])
    arguments = '\n'.join(arg for arg in sys.argv[1:])

    try:
        import pip
    except ImportError:
        packages = '`pip` not installed !'
    else:
        packages = '\n'.join(
            '{0} - {1}'.format(package.key, package.version)
            for package in pip.get_installed_distributions()
        )

    print(
        '```{0}Bug Report :\n'
        '`pockyt` has encountered an error ! '
        'Please submit this bug report at \n` {1} `.{0}'
        'Python Version : {2}{0}'
        'Installed Packages :\n{3}{0}'
        'Runtime Arguments :\n{4}{0}'
        'Error Message :\n{5}{0}```'.format(
            separator, API.ISSUE_URL, python_version,
            packages, arguments, message or traceback.format_exc().strip()
        )
    )


class SuppressedStdout(object):
    """
    Suppresses STDOUT, utilize with the `with` keyword
    """

    def __init__(self):
        self.orig_stdout = sys.stdout.fileno()
        self.copy_stdout = os.dup(self.orig_stdout)
        self.devnull = None

    def __enter__(self):
        self.devnull = open(os.devnull, 'w')
        os.dup2(self.devnull.fileno(), self.orig_stdout)

    def __exit__(self, *args):
        os.dup2(self.copy_stdout, self.orig_stdout)
        self.devnull.close()


class Network(object):
    """
    Safe POST Request, with error-handling
    """

    @staticmethod
    def post_request(link, payload):
        req = requests.post(link, json=payload)

        if req.status_code != 200:
            print_bug_report('API Error {0} ! : {1}'.format(
                req.headers.get('X-Error-Code'),
                req.headers.get('X-Error'),
            ))
            sys.exit(1)
        else:
            try:  # preserve json response ordering, as per API
                req.api_json = req.json(object_pairs_hook=OrderedDict)
            except ValueError:
                req.api_json = {}
            finally:
                return req


class Browser(object):
    """
    Silently open browser windows/tabs
    """

    @staticmethod
    def open(link, new=0, autoraise=True):
        with SuppressedStdout():
            webbrowser.open(
                url=link,
                new=new,
                autoraise=autoraise,
            )

    @classmethod
    def open_new_window(cls, link):
        cls.open(link, new=1)

    @classmethod
    def open_new_tab(cls, link):
        cls.open(link, new=2)
