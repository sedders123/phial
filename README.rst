phial
=====

|Documentation Status| |Github Actions| |Coverage Status| |PyPi|

    A lightweight framework for building slack bots

Phial is a slack bot framework, modelled loosely on
`flask <https://github.com/pallets/flask/>`__.


Table of Contents
-----------------

-  `Usage <#usage>`__
-  `Install <#install>`__
-  `Contribute <#contribute>`__
-  `Licenses <#licenses>`__

Usage
-----

Python:
~~~~~~~

.. code:: python

    from phial import Phial, command, Response

    bot = Phial('---slack token here---')

    @bot.command('greet <name>')
    def greet(name):
        '''A command with an argument which replies to a message'''
        return "Hello {0}".format(name)

    bot.run()

Slack:
~~~~~~

By default the bot requires a prefix of ``!`` before its commands. This
can be changed in the config.

::

    youruser:
    > !greet jim
    bot:
    > Hello Jim

Features:

-  Decorator based command definition
-  Send messages to slack
-  Reply to messages in a thread
-  Reply to messages with a reaction
-  Upload Files

Examples of commands utilising these features can be found in the
`examples <examples/>`__ folder

Install
-------

::

      $ pip install phial-slack

Contribute
----------

If a feature is missing, or you can improve the code please submit a PR
or raise an Issue

Licenses
--------

phial - MIT © 2019 James Seden Smith

Erlenmeyer Flask by Iconic from the Noun Project - `CC BY
3.0 <https://creativecommons.org/licenses/by/3.0/>`__ (used in
`examples/phial.png <examples/phial.png>`__)

.. |Documentation Status| image:: https://readthedocs.org/projects/phial/badge/?version=develop
   :target: http://phial.readthedocs.io/en/develop/
.. |Github Actions| image:: https://github.com/sedders123/phial/workflows/CI/badge.svg
   :target: https://github.com/sedders123/phial/actions
.. |Coverage Status| image:: https://codecov.io/gh/sedders123/phial/branch/develop/graph/badge.svg
   :target: https://codecov.io/gh/sedders123/phial/
.. |PyPi| image:: https://badge.fury.io/py/phial-slack.svg
    :target: https://badge.fury.io/py/phial-slack
