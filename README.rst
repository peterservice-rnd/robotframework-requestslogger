RobotFramework Requests Logging Library
=======================================

|Build Status|

Short Description
-----------------

`Robot Framework`_ library for logging HTTP requests and responses, based on `Requests`_ library.

Installation
------------

::

    pip install robotframework-requestslogger

Documentation
-------------

See keyword documentation for robotframework-requestslogger library in
folder ``docs``.

Example
-------
+-------------+--------------------------------+-----------------------------+------------------------+----------+
| Test cases  |              Action            |           Argument          |        Argument        | Argument |
+=============+================================+=============================+========================+==========+
| Simple Test | RequestsLibrary.Create session | Alias                       | http://www.example.com |          |
+-------------+--------------------------------+-----------------------------+------------------------+----------+
|             | ${response}=                   | RequestsLibrary.Get request | Alias                  | /        |
+-------------+--------------------------------+-----------------------------+------------------------+----------+
|             | RequestsLogger.Write log       | ${response}                 |                        |          |
+-------------+--------------------------------+-----------------------------+------------------------+----------+


License
-------

Apache License 2.0

.. _Robot Framework: http://www.robotframework.org
.. _Requests: http://docs.python-requests.org/en/latest

.. |Build Status| image:: https://travis-ci.org/peterservice-rnd/robotframework-requestslogger.svg?branch=master
   :target: https://travis-ci.org/peterservice-rnd/robotframework-requestslogger