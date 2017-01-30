from datetime import datetime as date, timedelta as timedelta
import time
from flask import request, current_app
from flaskbald.response import APIError, APIUnauthorized
from functools import wraps
import jwt
import json


def create_jwt(secret, payload={}, exp=date.utcnow() + timedelta(days=7),
               iat=date.utcnow(), algorithm='HS256'):
    payload.update({
        'exp': exp,
        'iat': iat
    })
    return jwt.encode(payload, secret, algorithm=algorithm)


def decode_jwt(token, secret, audience=None, algorithm='HS256'):
    if not audience:
        jwt.decode(token, secret, algorithm=algorithm)
    return jwt.decode(token, secret, audience=audience, algorithm=algorithm)


def _auth_error():
    raise APIUnauthorized("User authentication is required to access this resource.")


def get_jwt_claims(jwt_key='Authorization'):
    secret = current_app.config.get('JWT_CLIENT_SECRET')
    audience = current_app.config.get('JWT_AUDIENCE')

    if not secret:
        raise APIError("JWT secret not specified. Contact hello@mylestoned.com for assistance.")

    jwtoken = request.headers.get(jwt_key, request.cookies.get(jwt_key))
    if not jwtoken:
        _auth_error()

    try:
        jwt_claims = decode_jwt(jwtoken, secret, audience=audience)
    except (jwt.ExpiredSignatureError, jwt.DecodeError):
        _auth_error()

    sub = jwt_claims.get('sub')
    if not sub:
        _auth_error()

    return jwt_claims


def user_required(orig_func=None, jwt_key='jwt'):

    def requirement(orig_func):
        '''Requirement decorator.'''
        @wraps(orig_func)
        def replacement(*pargs, **kargs):
            get_jwt_claims(jwt_key=jwt_key)
            return orig_func(*pargs, **kargs)

        return replacement

    if not orig_func:
        return requirement
    else:
        return requirement(orig_func)


def get_auth_id(jwt_key='jwt'):
    '''Get the current logged-in users auth id'''
    try:
        jwt_claims = get_jwt_claims(jwt_key=jwt_key)
    except (APIError, APIUnauthorized):
        return None

    return jwt_claims.get('sub')
