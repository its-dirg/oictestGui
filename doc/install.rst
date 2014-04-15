Install
#######

This is a guide of how to install oictestGui

How to install oictestGui:
===========================

There are two ways to install the saml2testGui. First of you could install saml2testGui and all applications on which it depends manually. If you are running debian you could use an install script called Yais.

Manually:
---------

Linux/Mac:

    Open a terminal and enter::

        git clone https://github.com/its-dirg/saml2testGui [your local path]
        cd [your path]
        sudo python setup.py install

Dependencies:
^^^^^^^^^^^^^

The SAML2testGui depends on two applications: dirg-util, oictest

Install dirg-util
"""""""""""""""""

Linux/Mac:

    Open a terminal and enter::

        git clone https://github.com/its-dirg/dirg-util [your path]
        cd [your path]
        sudo python setup.py install

Install oictest:
"""""""""""""""""

Linux/Mac:

    Open a terminal and enter::

        git clone https://github.com/rohe/oictest [your path]
        cd [your path]
        sudo python setup.py install

 If you want to setup a simple test OP it's recommended that you install pyoidc a well.

Install pyoidc:
"""""""""""""""""

Linux/Mac:

    Open a terminal and enter::

        git clone https://github.com/rohe/pyoidc [your path]
        cd [your path]
        sudo python setup.py install


