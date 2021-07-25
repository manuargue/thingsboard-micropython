# Copyright 2021 Coredump Labs
#
# SPDX-License-Identifier: Apache-2.0

import pathlib
import sdist_upip
from setuptools import setup


HERE = pathlib.Path(__file__).parent
README = (HERE / 'README.md').read_text()

VERSION = '0.1.4'

setup(
    name='thingsboard-micropython',
    version=VERSION,
    description='ThingsBoard MQTT MicroPython client',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/coredumplabs/thingsboard-micropython',
    license='Apache Software License (Apache Software License 2.0)',
    author='Coredump Labs',
    author_email='info@coredumplabs.com',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: Implementation :: MicroPython',
    ],
    packages=['uthingsboard'],
    cmdclass={'sdist': sdist_upip.sdist},
    download_url=f'https://github.com/coredumplabs/thingsboard-micropython/releases/tag/v{VERSION}'
)
