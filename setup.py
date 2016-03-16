try:
	from setuptools import setup, find_packages
except ImportError:
	from ez_setup import use_setuptools
	use_setuptools()
	from setuptools import setup, find_packages

import io
import os

here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'README.md'), encoding='utf8') as f:
	README = f.read()

try:
	with io.open(os.path.join(here, 'CHANGELOG.md'), encoding='utf8') as f:
		CHANGES = f.read() or ''
except IOError:
	CHANGES = ''

from setuptools import setup

setup(name='flaskbald',
	version='1.0.0',
	description='Simple batteries included esque features.',
	long_description=README + '\n\n' + CHANGES,
	url='http://github.com/jfmyers01',
	author='Jim Myers',
	author_email='jfmyers01@gmail.com',
	license='MIT',
	packages=find_packages(),
	package_data={'flaskbald': ['default_templates/*.html']},
	install_requires=[
		'SQLAlchemy', 'Flask', 'Flask-SQLAlchemy', 'jinja2', 'phonenumbers', 'Flask-Cors', 'Flask-ErrorMail'
	],
	zip_safe=False)
