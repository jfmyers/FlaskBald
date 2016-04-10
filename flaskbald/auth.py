import jwt
from datetime import datetime as date, timedelta as timedelta


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
