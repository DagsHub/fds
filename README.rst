Furious Flemingo aka ``ff``
===========================
.. image:: https://circleci.com/gh/mohithg/furious-flemingo.svg?style=svg
    :target: https://app.circleci.com/pipelines/github/mohithg/furious-flemingo

.. image:: https://badge.fury.io/py/furiousflemingo-mohithg.svg
    :target: https://badge.fury.io/py/furiousflemingo-mohithg

``ff`` is a tool for Data Scientists made by DAGsHub to version control
data and code at once.

At the high level ``ff`` is a wrapper for Git and DVC. So Data
Scientists can use ``ff`` instead of ``git`` and ``dvc`` separately.

Commands Supported
------------------

+----------+-----------------------------+---------------+
| Syntax   | Description                 | Status        |
+==========+=============================+===============+
| init     | Initializes git and dvc     | In-Progress   |
+----------+-----------------------------+---------------+
| status   | Get status of git and dvc   | TODO          |
+----------+-----------------------------+---------------+

Installation
------------

TBD

Docker support
--------------

TBD

Dev instructions
----------------

-  Test your setup.py
-  ``python3 setup.py install``
-  Build your package
-  ``python3 setup.py sdist``
-  Publish your package
-  ``twine upload dist/*``

