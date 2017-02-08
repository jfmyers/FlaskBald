from datetime import datetime as date, timedelta as timedelta
import time
from flask import request, current_app, redirect
from flaskbald.response import APIError, APIUnauthorized
from functools import wraps
import jwt
import json
import logging


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


def get_jwt_claims(jwt_key='Authorization'):
    logging.info("get_jwt_claims")
    secret = current_app.config.get('JWT_CLIENT_SECRET')
    logging.info("secret: {0}".format(secret))
    audience = current_app.config.get('JWT_CLIENT_AUDIENCE')
    logging.info("audience: {0}".format(audience))

    if not secret:
        return None

    jwtoken = request.headers.get(jwt_key, request.cookies.get(jwt_key))
    logging.info("Request Headers: ")
    logging.info(request.headers)
    logging.info("jwtoken: {0}".format(jwtoken))
    if not jwtoken:
        return None

    try:
        jwt_claims = decode_jwt(jwtoken, secret, audience=audience)
    except (jwt.ExpiredSignatureError, jwt.DecodeError):
        logging.info("JWT signature error")
        return None

    sub = jwt_claims.get('sub')
    logging.info("Sub: {0}".format(sub))
    if not sub:
        return None

    return jwt_claims


def user_required(orig_func=None, jwt_key='Authorization', redirect_url=None, code=302):

    def requirement(orig_func):
        '''Requirement decorator.'''
        @wraps(orig_func)
        def replacement(*pargs, **kargs):
            jwt_claims = get_jwt_claims(jwt_key=jwt_key)
            if not jwt_claims:
                if redirect_url:
                    if type(redirect_url) != str:
                        redirect_url = redirect_url(request)
                    return redirect(redirect_url, code=code)
                else:
                    raise APIUnauthorized("User authentication is required to access this resource.")
            return orig_func(*pargs, **kargs)

        return replacement

    if not orig_func:
        return requirement
    else:
        return requirement(orig_func)


def get_auth_id(jwt_key='Authorization'):
    '''Get the current logged-in users auth id'''
    try:
        jwt_claims = get_jwt_claims(jwt_key=jwt_key)
    except (APIError, APIUnauthorized):
        return None

    return jwt_claims.get('sub')
