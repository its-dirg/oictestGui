# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name="oictestGui",
    version="0.1",
    description='Gui for oictest',
    author = "Hans, Hoerberg och Daniel Evertsson",
    author_email = "hans.horberg@umu.se, daniel.evertsson@umu.se",
    license="Apache 2.0",
    packages=['oictestGui'],
    package_dir = {"": "src"},
    classifiers = ["Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Libraries :: Python Modules"],
    install_requires = ['requests', 'pyoidc',
                        "cherrypy", "mako", "pyjwkest", "beaker"],

    zip_safe=False,
)