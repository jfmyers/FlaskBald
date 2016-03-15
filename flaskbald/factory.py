#!/usr/bin/env python
# encoding: utf-8
from flask import Flask, render_template, request
from db_ext import db
from celery_ext import celery
from response import APINotFound, api_action
from log import default_debug_log
from flask.ext.cors import CORS, cross_origin
import os
import jinja2


ALLOWED_HOSTS = 'ALLOWED_HOSTS'
ALL_HOSTS = '*'


def load_config(app, config_file=None, env='development'):
	if not config_file:
		return app

	app.config.from_pyfile(config_file)
	if not app.config.get(ALLOWED_HOSTS):
		app.config.update({ALLOWED_HOSTS: ALL_HOSTS})

	return app

	# var = 'APP_ENV'
	# if env is None and var in os.environ:
	# 	env = os.environ[var]

	# if env in config_files:
	# 	app.config.from_pyfile(config_files[env])

	# return app


def setup_templates(app, custom_template_path=None):
	base_template_dir = os.path.join(
		os.path.abspath(os.path.dirname(__file__)),
		'default_templates'
	)

	template_paths = [
		app.jinja_loader,
		jinja2.FileSystemLoader(base_template_dir)]

	if custom_template_path:
		template_paths.append(
			jinja2.FileSystemLoader(custom_template_path)
		)

	app.jinja_loader = jinja2.ChoiceLoader(template_paths)
	return app


def register_blue_prints(app, blue_prints):
	for module in blue_prints:
		app.register_blueprint(module)
	return app


def setup_debug_log(app):
	(app.config.get('DEBUG', False) == True and default_debug_log())
	return app


def error_endpoints(app, custom_error_endpoints=False):
	if custom_error_endpoints is True:
		return app

	@app.errorhandler(404)
	def not_found(error):
		return render_template('404.html'), 404

	@app.errorhandler(500)
	def not_found(error):
		return render_template('500.html'), 500

	return app


def before_handler(app, custom_handler, custom_handler_args, custom_handler_kargs):

	if custom_handler:
		@app.before_request
		def before_request():
			custom_handler(*custom_handler_args, **custom_handler_kargs)

		return app

	@app.before_request
	def before_request():
		origin_request = request.from_values()
		if app.config[ALLOWED_HOSTS] != ALL_HOSTS and origin_request.host not in app.config[ALLOWED_HOSTS]:
			if app.config.get('DEBUG', app.config.get('debug')):
				return APINotFound(message="Invalid host: '{0}'".format(origin_request.host))
			else:
				return APINotFound()

	return app


def after_handler(app, custom_handler, custom_handler_args, custom_handler_kargs):

	if custom_handler:
		@app.after_request
		def after_request(response):
			custom_handler_kargs['response'] = response
			return custom_handler(*custom_handler_args, **custom_handler_kargs)

		return app

	@app.after_request
	def after_request(response):
		# Commit the session
		db.session.commit()

		# Close the session
		db.session.close()

		# Return the response object
		return response

	return app


def init_db(app):
	db.init_app(app)
	return app


def create_app(config_file, blue_prints=[], custom_error_endpoints=False,
			   custom_template_path=None, custom_before_handler=None,
			   custom_before_handler_args=[], custom_before_handler_kargs={},
			   custom_after_handler=None, custom_after_handler_args=[],
			   custom_after_handler_kargs={}, template_folder=None,
			   cors=True):

	if config_file is None:
		raise(Exception("Hey, 'config_files' cannot be 'None'!"))

	app = Flask(__name__) if not template_folder else Flask(__name__, template_folder=template_folder)
	app = load_config(app, config_file)
	app = setup_templates(app, custom_template_path)
	app = setup_debug_log(app)
	app = register_blue_prints(app, blue_prints)
	app = error_endpoints(app, custom_error_endpoints)
	app = before_handler(app, custom_before_handler, custom_before_handler_args, custom_before_handler_kargs)
	app = after_handler(app, custom_after_handler, custom_after_handler_args, custom_after_handler_kargs)
	app = init_db(app)

	if cors is True:
		print ""
		print "Activating CORS!!!"
		print ""
		cors = CORS(app)
		app.config['CORS_HEADERS'] = 'Content-Type'

	return app


def create_celery_app(app):
    celery.init_app(app)
    return celery


	# return (
	# 	init_db(
	# 		after_handler(
	# 			before_handler(
	# 				error_endpoints(
	# 					register_blue_prints(
	# 						setup_debug_log(
	# 							setup_templates(
	# 								load_config(
	# 									Flask(__name__),
	# 									config_file
	# 								),
	# 								custom_template_path
	# 							)
	# 						),
	# 						blue_prints
	# 					),
	# 					custom_error_endpoints
	# 				),
	# 				custom_before_handler,
	# 				custom_before_handler_args,
	# 				custom_before_handler_kargs
	# 			),
	# 			custom_after_handler,
	# 			custom_after_handler_args,
	# 			custom_after_handler_kargs
	# 		)
	# 	)
	# )
