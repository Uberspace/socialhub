import sys
from os import path

try:
    from setuptools import setup
except ImportError:
    print('socialhub needs setuptools.', file=sys.stderr)
    print('Please install it using your package-manager or pip.', file=sys.stderr)
    sys.exit(1)

root_dir = path.abspath(path.dirname(__file__))

setup(
    name='socialhub',
    version='0.1.0',
    description='API client for socialhub.io',
    author='uberspace.de',
    author_email='hallo@uberspace.de',
    url='https://github.com/uberspace/socialhub',
    long_description=open(root_dir + '/README.md').read(),
    long_description_content_type='text/markdown',
    packages=[
        'socialhub',
    ],
    install_requires=[
        'requests',
        'dataclasses',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Customer Service',
        'Intended Audience :: Information Technology',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    zip_safe=True,
)
