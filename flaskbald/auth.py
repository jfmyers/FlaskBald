from datetime import datetime as date, timedelta as timedelta
from flask import request, current_app
from flaskbald.response import APIError, APIUnauthorized
import jwt


def create_jwt(secret, payload={}, exp=date.utcnow() + timedelta(days=7),
			   iat=date.utcnow(), handle='mrbayes',
			   algorithm='HS256'):
	payload.update({
		'exp': exp,
		'iat': iat,
		'handle': handle
	})
	return jwt.encode(payload, secret, algorithm=algorithm)


def decode_jwt(token, secret, algorithm='HS256'):
	return jwt.decode(token, secret, algorithm=algorithm)


def user_required(jwt_cookie_key='jwt'):

	def _auth_error():
		raise APIUnauthorized("User authentication is required to access this resource.")

	def requirement(action_method):
		'''Requirement decorator.'''

		@wraps(action_method)
		def replacement(self, *pargs, **kargs):
			start_time = date.utcnow()
			secret = current_app.config.get('JWT_AUTH_SECRET')
			if not secret:
				raise APIError("JWT secret not specified. Contact hello@mylestoned.com for assistance.")

			jwt = request.cookies.get(jwt_cookie_key)
			if not jwt:
				_auth_error()

			decoded = decode_jwt(jwt, secret)
			exp = decoded.get('exp')

			if not exp or start_time > exp:
				_auth_error()

			user_id = decoded.get('user_id')
			if not user_id:
				_auth_error()

			# Get the user
			try:
				user = User.get(id=user_id)
			except User.NotFound:
				_auth_error()

		return replacement
	return requirement
