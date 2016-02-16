#!/usr/bin/env python
# encoding: utf-8
from webob import Response
from functools import wraps
import json


# # action / method decorator
# def action(method):
#     '''
#     Decorates methods that are WSGI apps to turn them into pybald-style actions.

#     :param method: A method to turn into a pybald-style action.

#     This decorator is usually used to take the method of a controller instance
#     and add some syntactic sugar around it to allow the method to use WebOb
#     Request and Response objects. It will work with any method that
#     implements the WSGI spec.

#     It allows actions to work with WebOb request / response objects and handles
#     default behaviors, such as displaying the view when nothing is returned,
#     or setting up a plain text Response if a string is returned. It also
#     assigns instance variables from the ``pybald.extension`` environ variables
#     that can be set from other parts of the WSGI pipeline.

#     This decorator is optional but recommended for making working
#     with requests and responses easier.
#     '''
#     # the default template name is the controller class + method name
#     # the method name is pulled during decoration and stored for use
#     # in template lookups
#     template_name = method.__name__
#     # special case where 'call' or 'index' use the base class name
#     # for the template otherwise use the base name
#     if template_name in ('index', '__call__'):
#         template_name = ''

#     @wraps(method)
#     def action_wrapper(self, environ, start_response):
#         req = Request(environ)
#         # add any url variables as members of the controller
#         for varname, value in req.urlvars.items():
#             # Set the controller object to contain the url variables
#             # parsed from the dispatcher / router
#             setattr(self, varname, value)

#         # # add the pybald extension dict to the controller
#         # # object
#         # for key, value in req.environ.setdefault('pybald.extension', {}).items():
#         #     setattr(self, key, value)

#         # TODO: fixme this is a hack
#         setattr(self, 'request', req)
#         setattr(self, 'request_url', req.url)

#         # set pre/post/view to a no-op if they don't exist
#         pre = getattr(self, '_pre', noop_func)
#         post = getattr(self, '_post', noop_func)

#         # # set the template_id for this request
#         # self.template_id = get_template_name(self, template_name)

#         # # The response is either the controllers _pre code, whatever
#         # # is returned from the controller
#         # # or the view. So pre has precedence over
#         # # the return which has precedence over the view
#         # resp = (pre(req) or
#         #          method(self, req) or
#         #          context.render(template=self.template_id,
#         #                      data=self.__dict__ or {}))
#         # # if the response is currently a string
#         # # wrap it in a response object
#         # if isinstance(resp, str) or isinstance(resp, bytes):
#         #     resp = Response(body=resp, charset="utf-8")
#         # # run the controllers post code
#         # post(req, resp)
#         return resp(environ, start_response)
#     return action_wrapper

def json_response(body, status):
    '''
    Return response JSON encoded with proper headers.
    '''
    resp = Response(json.dumps({"status": "success", "data": body}),
                    status=status,
                    content_type="application/json",
                    charset="UTF-8")
    resp.headers.update({
        'Access-Control-Allow-Origin': '*',
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
