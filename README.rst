ownCloud News Updater
=====================

ownCloud does not require people to install threading or multiprocessing
libraries. Because the feed update process is mainly limited by I/O, parallel
fetching of RSS feed updates can speed up the updating process significantly.

In addition, Web Cron is not a supported cron setting since the update
process may time out.

Therefore the News app provides an API that offers a more fine grained
control over updating feeds. This Python project implements an update
mechanism that is based on the `updater REST API <https://github.com/owncloud/news/wiki/Updater-1.2>`_ or (new in 8.1.0) the
console based update API.

Pre-Installation
----------------

To run the updates via an external threaded script the cron updater has to be
disabled. To do that go to the admin section an uncheck the **Use ownCloud
cron** checkbox or open **owncloud/data/news/config/config.ini** and set::

    useCronUpdates = true

to::

    useCronUpdates = false

Installation
------------
There are two different ways to install the updater:
* Installation using pip
* Manual installation
* No installation

Installation using pip
~~~~~~~~~~~~~~~~~~~~~~
Since 8.2 the package is available on pypi for installation via pip (the
Python library package manager).

To install pip on your distribution of choice, `consolidate the pip
documentation <http://python-packaging-user-guide.readthedocs
.org/en/latest/install_requirements_linux/>`_

..note :: You need to install the Python3 version of pip

After installing pip, run::

    pip3 install owncloud-news-updater

To update the library, run::

    pip3 install --upgrade owncloud-news-updater

Manual installation
~~~~~~~~~~~~~~~~~~~
If you don't want to install the updater via pip, you can install it manually.
This requires setuptools to be installed. On Ubuntu this can be done by running::

    sudo apt-get install python3-setuptools

Then install the package like this::

    python3 setup.py install

No installation
~~~~~~~~~~~~~~~
If you do not want to install the script at all you can call it directly. This
however requires you to have the requests module to be installed. To do that
either get the package from your distro or use pip to install it. On Ubuntu this would be::

    sudo apt-get install python3-requests

or via pip:

    sudo pip3 install -r requirements.txt

Usage
-----

There are two ways to run the updater:
* Using the console API (recommended)::

    owncloud-news-updater /path/to/owncloud

* Using the REST API (when running the updater on a different machine)::

    owncloud-news-updater https://domain.com/path/to/owncloud --user admin_user --password admin_password

..note :: **admin_user** is a user id with admin rights, **admin_password** the user's password

You can view all options by running::

    owncloud-news-updater --help

usage: __main__.py [-h] [--testrun] [--threads THREADS] [--timeout TIMEOUT]
                   [--interval INTERVAL] [--loglevel {info,error}]
                   [--config CONFIG] [--user USER] [--password PASSWORD]
                   [url]

positional arguments:
  url                   The URL or absolute path to the directory where
                        owncloud is installed. Must be specified on the
                        command line or in the config file. If the URL starts
                        with http:// or https://, a user and password are
                        required. Otherwise updater tries to use the console
                        based API which was added in 8.1.0

optional arguments:
  -h, --help            show this help message and exit
  --testrun             Run update only once, DO NOT use this in a cron job,
                        only recommended for testing
  --threads THREADS, -t THREADS
                        How many feeds should be fetched in parallel, defaults
                        to 10
  --timeout TIMEOUT, -s TIMEOUT
                        Maximum number of seconds for updating a feed,
                        defaults to 5 minutes
  --interval INTERVAL, -i INTERVAL
                        Update interval between fetching the next round of
                        updates in seconds, defaults to 15 minutes. The update
                        timespan will be subtracted from the interval.
  --loglevel {info,error}, -l {info,error}
                        Log granularity, info will log all urls and received
                        data, error will only log errors
  --config CONFIG, -c CONFIG
                        Path to config file where all parameters except can be
                        defined as key values pair. An example is in
                        bin/example_config.ini
  --user USER, -u USER  Admin username to log into ownCloud. Must be specified
                        on the command line or in the config file if the
                        updater should update over HTTP
  --password PASSWORD, -p PASSWORD
                        Admin password to log into ownCloud if the updater
                        should update over HTTP



You can also put your settings in a config file, looking like this:

.. code:: ini

    [updater]
    user = admin
    password = admin
    threads = 10
    interval = 900
    loglevel = error
    testrun = false
    url = http://localhost/owncloud

Then run the updater with::

    owncloud-news-updater -c /path/to/config


Running the updater as SystemD service
--------------------------------------
Since almost always you want to run and stop the updater using your in init system,
the updater contains a simple example SystemD service file in
**systemd/owncloud-news-updater.service**. To install it, copy the file into the
**/etc/systemd/system/** folder and run::

    systemctl enable owncloud-news-updater.service
    systemctl start owncloud-news-updater.service


Self signed certificates
------------------------

Should you use a self signed certificate over SSL, first consider getting a free valid cert signed by `StartSSL <http://startssl.com>`_. If you don't want to get a valid certificate, you need to add it to the installed certs::

    cat /path/to/your/cert/cacert.pem >> /usr/local/lib/python3.X/dist-packages/requests/cacert.pem

The directories might vary depending on your distribution and Python version.
