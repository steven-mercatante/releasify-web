# TODO: organize Resources into their own package
# TODO: organize Middleware into their own package
# TODO: organize error handler and helper functions into their own package(es)
import base64
import json
import logging
import os
import re
import sys

import falcon
from releasify.client import (
    Client, 
    InvalidReleaseTypeError,
    NoCommitsError,
    NotFoundError,
    UnauthorizedError,
)

from .constants import INVALD_LOG_LEVEL_ERR
from .exceptions import (
    MissingRequiredArgError, 
    JSONBodyRequiredError,
)
from .utils import boolify


if os.getenv('LOG_LEVEL'):
    log_level = os.getenv('LOG_LEVEL').upper()
else:
    log_level = logging.WARNING

try:    
    logging.basicConfig(level=log_level)
except ValueError:
    sys.exit(INVALD_LOG_LEVEL_ERR.format(log_level=log_level))


class AuthMiddleware(object):
    def process_request(self, req, resp):
        if req.path in ('/', '/healthcheck'):
            return

        auth = req.get_header('Authorization')
        if auth is None:
            raise falcon.HTTPUnauthorized('Please provide a username and password')

        if not auth.startswith('Basic '):
            raise falcon.HTTPUnauthorized('Basic auth required')

        token = auth.replace('Basic ', '')
        user, password = base64.urlsafe_b64decode(token).decode('utf-8').split(':')

        req.context['user'] = user
        req.context['password'] = password


class HealthCheckResource(object):
    def on_get(self, req, resp):
        resp.media = {'ok': True}


class IndexResource(object):
    def on_get(self, req, resp):
        # TODO: return actual HTML
        resp.status = falcon.HTTP_200
        resp.content_type = 'text/html'
        resp.body = """
        Hi there! This is the index route of the Releasify API.
        You're probably looking for the /releases endpoint.
        There's also a handy /healthcheck endpoint if you just want to test that the API is running.
        """


class ReleaseResource(object):
    @staticmethod
    def _convert_status_code(status_code):
        try:
            return getattr(falcon, f'HTTP_{status_code}')
        except (AttributeError):
            return falcon.HTTP_500

    def on_post(self, req, resp):
        try:
            payload = json.load(req.bounded_stream)
        except json.decoder.JSONDecodeError:
            raise JSONBodyRequiredError

        owner = get_required_arg(payload, 'owner')
        repo = get_required_arg(payload, 'repo')
        release_type = get_required_arg(payload, 'type')
        dry_run = boolify(payload.get('dry_run'))
        force_release = boolify(payload.get('force'))
        draft = boolify(payload.get('draft'))
        prerelease = boolify(payload.get('prerelease', True))
        target_branch = payload.get('target_branch')

        client = Client(req.context['user'], req.context['password'])

        result = client.create_release(owner, repo, release_type, draft, prerelease, dry_run, force_release, target_branch)
        resp.status = self._convert_status_code(result['resp'].status_code)

        resp.media = {
            'body': result['body'],
            'tag_name': result['tag_name'],
            'dry_run': result['dry_run'],
            'prerelease': result['prerelease'],
        }


def get_required_arg(args, arg_name):
    try:
        return args[arg_name]
    except (KeyError):
        raise MissingRequiredArgError(arg_name)


def handle_error(exception, req, resp, params):
    """Map custom exceptions to Falcon exceptions"""
    if isinstance(exception, UnauthorizedError):
        raise falcon.HTTPUnauthorized()
    elif isinstance(exception, (InvalidReleaseTypeError, NoCommitsError)):
        raise falcon.HTTPError(status=falcon.HTTP_400, description=str(exception))
    elif isinstance(exception, NotFoundError):
        raise falcon.HTTPNotFound()
    elif isinstance(exception, falcon.HTTPBadRequest):
        raise
    else:
        raise falcon.HTTPInternalServerError(description=str(exception))


def create_api():
    api = falcon.API(middleware=[AuthMiddleware()])
    api.add_error_handler(Exception, handle_error)
    api.add_route('/', IndexResource())
    api.add_route('/healthcheck', HealthCheckResource())
    api.add_route('/releases', ReleaseResource())
    return api


api = create_api()
