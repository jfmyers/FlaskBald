from flask import Flask, render_template
from db_ext import db
from log import default_debug_log
import os
import jinja2


def load_config(app, config_file=None, env='development'):
	if not config_file:
		return app

	app.config.from_pyfile(config_file)
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


def init_db(app):
	db.init_app(app)
	return app


def create_app(config_file, blue_prints=[], custom_error_endpoints=False, 
			   custom_template_path=None):

	if config_file is None:
		raise(Exception("Hey, 'config_files' cannot be 'None'!"))

	return (
		init_db(
			error_endpoints(
				register_blue_prints(
					setup_debug_log(
						setup_templates(
							load_config(
								Flask(__name__),
								config_file
							),
							custom_template_path
						)
					),
					blue_prints
				),
				custom_error_endpoints
			)
		)
	)
