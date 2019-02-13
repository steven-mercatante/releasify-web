import base64
import json
import logging
import os
import sys

import falcon

from .client import (
    Client, 
    InvalidReleaseTypeError,
    NoCommitsError,
    NotFoundError,
    UnauthorizedError,
)
from .constants import INVALD_LOG_LEVEL_ERR
from .utils import boolify

if os.getenv('LOG_LEVEL'):
    log_level = os.getenv('LOG_LEVEL').upper()
else:
    log_level = logging.WARNING

try:    
    logging.basicConfig(level=log_level)
except ValueError:
    sys.exit(INVALD_LOG_LEVEL_ERR.format(log_level=log_level))


class MissingRequiredArgError(Exception):
    def __init__(self, arg):
        message = f'You\'re missing the required `{arg}` argument'
        super(MissingRequiredArgError, self).__init__(message)


class AuthMiddleware(object):
    def process_request(self, req, resp):
        auth = req.get_header('Authorization')
        if auth is None:
            raise falcon.HTTPUnauthorized('Please provide a username and password')

        if not auth.startswith('Basic '):
            raise falcon.HTTPUnauthorized('Basic auth required')

        token = auth.replace('Basic ', '')
        user, password = base64.urlsafe_b64decode(token).decode('utf-8').split(':')

        req.context['user'] = user
        req.context['password'] = password


class ReleaseResource(object):
    @staticmethod
    def _convert_status_code(status_code):
        try:
            return getattr(falcon, f'HTTP_{status_code}')
        except (AttributeError):
            return falcon.HTTP_500

    def on_post(self, req, resp):
        payload = json.load(req.bounded_stream)

        owner = get_required_arg(payload, 'owner')
        repo = get_required_arg(payload, 'repo')
        release_type = get_required_arg(payload, 'release_type')
        dry_run = boolify(payload.get('dry_run'))
        force_release = boolify(payload.get('force_release'))
        draft = boolify(payload.get('draft'))
        prerelease = boolify(payload.get('prerelease'))
        target_branch = payload.get('target_branch')

        client = Client(req.context['user'], req.context['password'])

        result = client.create_release(owner, repo, release_type, draft, prerelease, dry_run, force_release, target_branch)
        resp.status = self._convert_status_code(result['resp'].status_code)

        resp.media = {
            'body': result['body'],
            'tag_name': result['tag_name'],
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
    else:
        raise falcon.HTTPInternalServerError(description=str(exception))


def create_api():
    api = falcon.API(middleware=[AuthMiddleware()])
    api.add_error_handler(Exception, handle_error)
    api.add_route('/releases', ReleaseResource())
    return api


api = create_api()
