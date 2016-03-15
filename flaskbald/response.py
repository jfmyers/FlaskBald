#!/usr/bin/env python
# encoding: utf-8
from webob import Response
from functools import wraps
import json
from flask.ext.cors import CORS, cross_origin


def json_response(body, status):
    '''
    Return response JSON encoded with proper headers.
    '''
    resp = Response(json.dumps({"status": "success", "data": body}),
                    status=status,
                    content_type="application/json",
                    charset="UTF-8")
    resp.headers.update({
        # 'Access-Control-Allow-Origin': '*',
        'Access-Control-Expose-Headers': 'Access-Control-Allow-Origin',
        'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept',
    })
    return resp


def api_action(orig_func):
	"""
	Decorator that wraps an action in API goodness.

	The orig_func is expected to return any JSON-serializable python data
	structure, or raise any ApiException (which will be wrapped in a
	standard JSON structure).

	"""
	@wraps(orig_func)
	@cross_origin()
	def replacement(*args, **kargs):
		try:
			handler_response = orig_func(*args, **kargs)
		except APIError as api_error_response:
			return api_error_response

		# return the response or reformat for proper response
		if isinstance(handler_response, Response):
			return handler_response
		else:
			return json_response(handler_response, status='200 OK')

	return replacement


def request_data():
	'''
	Retrieve the data from this Flask app's context,
	decode and return as Python dict.
	'''
	from flask import request
	data = request.get_data()
	if data is None:
		data = {}
	else:
		try:
			data = json.loads(data)
		except ValueError:
			data = {}
	return data


class APIException(Exception):
    '''Base exception class for all Mylestoned API exceptions'''
    def __init__(self, message):
        self.message = message or self.message
        super(APIException, self).__init__(self.message)


class WSGIAPIException(Response, APIException):
    '''
    A multi-inherited exception object that also acts as as
    web response. The returned exception can be returned and
    rendered as part of the WSGI pipeline.
    '''
    def __init__(self, message=None, *pargs, **kargs):
        APIException.__init__(self, message)
        if self.http_status and 'status' not in kargs:
            kargs['status'] = self.http_status
        kargs.update({'content_type': "application/json",
                      'charset': "UTF-8"})
        super(WSGIAPIException, self).__init__(*pargs, **kargs)
        # Response.__init__(self, *pargs, **kargs)
        # for now, all smarterer API calls are responded to as
        # JSON
        # self.content_type = "application/json"
        # self.charset = "UTF-8"
        message = self.body or self.message or self.status
        self.data = {'status': 'error', 'message': message, 'code': self.http_status}
        self.body = json.dumps(self.data)

    def __str__(self):
        return self.message or self.status


class APIError(WSGIAPIException):
    """
    Abstract class for Client Site API errors
    """
    http_status = 500


class APIPaymentRequired(APIError):
    http_status = 402


class APINotFound(APIError):
    http_status = 404


class APIBadRequest(APIError):
    http_status = 400


class APIUnauthorized(APIError):
    http_status = 401


class APIUserUnsubscribed(APIUnauthorized):
    """
    Indicates that the targeted User account is no longer
    subscribed to an API service

    (Inherits 401/Unauthorized status)
    """
