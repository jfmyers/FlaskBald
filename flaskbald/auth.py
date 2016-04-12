from datetime import datetime as date, timedelta as timedelta
import time
from flask import request, current_app
from flaskbald.response import APIError, APIUnauthorized
from functools import wraps
import jwt
import json


def create_jwt(secret, payload={}, exp=date.utcnow() + timedelta(days=7),
			   iat=date.utcnow(), handle='mrbayes', algorithm='HS256'):
	payload.update({
		'exp': exp,
		'iat': iat,
		'handle': handle
	})
	return jwt.encode(payload, secret, algorithm=algorithm)


def decode_jwt(token, secret, algorithm='HS256'):
	return jwt.decode(token, secret, algorithm=algorithm)


def user_required(orig_func=None, jwt_cookie_key='jwt'):

	def _auth_error():
		raise APIUnauthorized("User authentication is required to access this resource.")

	def requirement(orig_func):
		'''Requirement decorator.'''
		@wraps(orig_func)
		def replacement(*pargs, **kargs):
			secret = current_app.config.get('JWT_AUTH_SECRET')
			if not secret:
				raise APIError("JWT secret not specified. Contact hello@mylestoned.com for assistance.")

			jwtoken = request.cookies.get(jwt_cookie_key)
			if not jwtoken:
				_auth_error()

			try:
				decoded = decode_jwt(jwtoken, secret)
			except jwt.ExpiredSignatureError:
				_auth_error()

			user_id = decoded.get('user_id')
			if not user_id:
				_auth_error()

			return orig_func(*pargs, **kargs)

		return replacement

	if not orig_func:
		return requirement
	else:
		return requirement(orig_func)

