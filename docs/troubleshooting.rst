Troubleshooting
===============

Using supervisord for development
---------------------------------

On an ubuntu machine you can install supervisord with

.. code-block:: bash

   >sudo apt-get install supervisor

To start supervisord with an arbitrary configuration, you can type:

.. code-block:: bash

   >supervisord -c my_config_file.conf

You can find a supervisord config file inside the deployment/supervisord folder.
That config file contains a section for each service that you may want to run.
Feel free to comment one or more of those sections if you don't need that specific service.
If you just want to access the restful api or the admin for example, comment all those sections but the one
related to gunicorn.
You can stop supervisord (and all processes he's taking care of) with ctrl+c.
Please note that for some reason you may need to manually kill the celery worker when it's under heavy load.

Where are my log files?
-----------------------

You can find the various services log files under
  * /var/log/celery
  * /var/log/gunicorn

You may also want to inspect the main treeherder log file ~/treeherder-service/treeherder.log
