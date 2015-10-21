from setuptools import setup, find_packages

PACKAGE = "nginxparser"
NAME = "nginxparser"
DESCRIPTION = "Nginx log parser"
AUTHOR = "Timur Isanov"
AUTHOR_EMAIL = "tisanov@yahoo.com"
URL = "https://github.com/xtimon/nginx_parser"
VERSION = __import__(PACKAGE).__version__

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=open("README.md").read(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="GPL",
    url=URL,
    packages=find_packages(),
    entry_points={
        'console_scripts':
            ['nginxparser = nginxparser.core:main']
        }
)
