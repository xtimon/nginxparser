from setuptools import setup, find_packages

PACKAGE = "nginxparser"
NAME = "nginxparser"
DESCRIPTION = "Nginx log parser and analyzer"
AUTHOR = "Timur Isanov"
AUTHOR_EMAIL = "tisanov@yahoo.com"
URL = "https://github.com/xtimon/nginxparser"
VERSION = __import__(PACKAGE).__version__

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=open("README.rst").read(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="MIT",
    url=URL,
    packages=find_packages(),
    classifiers=[
        'Topic :: Internet :: Log Analysis',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    entry_points={
        'console_scripts':
            ['nginxparser = nginxparser.core:main']
        }
)
