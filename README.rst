ownCloud News Updater
=====================

.. image:: https://img.shields.io/pypi/v/owncloud_news_updater.svg
    :target: https://pypi.python.org/pypi/owncloud_news_updater
.. image:: https://travis-ci.org/owncloud/news-updater.svg?branch=master
    :target: https://travis-ci.org/owncloud/news-updater

This Python library is a parllel feed updater for the `ownCloud News app <https://github.com/owncloud/news>`_

ownCloud does not require people to install threading or multiprocessing
libraries. Because the feed update process is mainly limited by I/O, parallel
fetching of RSS feed updates can speed up the updating process significantly.

In addition, Web Cron is not a supported cron setting since the update
process may time out.

Therefore the News app provides an API that offers a more fine grained
control over updating feeds. This Python project implements an update
mechanism that is based on the `updater REST API <https://github.com/owncloud/news/wiki/Updater-1.2>`_ or (new in ownCloud News 8.1.0) the
console based update API.

.. contents:: :local:

Dependencies
------------

* **Python >=3.2**


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

* Installation using pip (recommended)
* Manual installation
* No installation

Installation Using Pip
~~~~~~~~~~~~~~~~~~~~~~
Since 8.2 the package is available on pypi for installation via pip (the
Python library package manager).

To install pip on your distribution of choice, `consolidate the pip
documentation <http://python-packaging-user-guide.readthedocs
.org/en/latest/install_requirements_linux/>`_

**Note**: You need to install the Python 3 version of pip

After installing pip, run::

    sudo pip3 install owncloud_news_updater --install-option="--install-scripts=/usr/bin"

To update the library, run::

    sudo pip3 install --upgrade owncloud_news_updater --install-option="--install-scripts=/usr/bin"

To uninstall the library run::

    sudo pip3 uninstall owncloud_news_updater

Manual Installation
~~~~~~~~~~~~~~~~~~~
If you don't want to install the updater via pip, you can install it manually.
This requires setuptools to be installed. On Ubuntu this can be done by running::

    sudo apt-get install python3-setuptools

Then install the package like this::

    python3 setup.py install --install-scripts=/usr/bin

To uninstall the updater run::

    python3 setup.py uninstall

No Installation
~~~~~~~~~~~~~~~
If you do not want to install the script at all you can call it directly.

Simply run the updater using::

    python3 -m owncloud_news_updater /path/to/owncloud

Usage
-----

There are two ways to run the updater:

* Using the console API (recommended)::

    owncloud-news-updater /path/to/owncloud

* Using the REST API (when running the updater on a different machine than ownCloud)::

    owncloud-news-updater https://domain.com/path/to/owncloud --user admin_user --password admin_password

**Note**: **admin_user** is a user id with admin rights, **admin_password** the user's password

You can view all options by running::

    owncloud-news-updater --help

::

    usage: owncloud-news-updater [-h] [--testrun] [--threads THREADS] [--timeout TIMEOUT]
                       [--interval INTERVAL] [--apilevel {v1-2,v2}]
                       [--loglevel {info,error}] [--config CONFIG]
                       [--phpini PHPINI] [--user USER] [--password PASSWORD]
                       [--version]
                       [url]

    positional arguments:
      url                   The URL or absolute path to the directory where
                            owncloud is installed. Must be specified on the
                            command line or in the config file. If the URL starts
                            with http:// or https://, a user and password are
                            required. Otherwise the updater tries to use the
                            console based API which was added in 8.1.0

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
      --apilevel {v1-2,v2}, -a {v1-2,v2}
                            API level. Use v2 for News 9.0.0 or greater, v1-2 for
                            lower versions
      --loglevel {info,error}, -l {info,error}
                            Log granularity, info will log all urls and received
                            data, error will only log errors
      --config CONFIG, -c CONFIG
                            Path to config file where all parameters except can be
                            defined as key values pair. An example is in
                            bin/example_config.ini
      --phpini PHPINI, -P PHPINI
                            Custom absolute path to the php.ini file to use for the
                            command line updater. If omitted, the default one will
                            be used
      --user USER, -u USER  Admin username to log into ownCloud. Must be specified
                            on the command line or in the config file if the
                            updater should update over HTTP
      --password PASSWORD, -p PASSWORD
                            Admin password to log into ownCloud if the updater
                            should update over HTTP
      --version, -v         Prints the updater's version



You can also put your settings in a config file, looking like this:

.. code:: ini

    [updater]
    user = admin  # only needed when using the REST API
    password = admin  # only needed when using the REST API
    threads = 10
    interval = 900
    loglevel = error
    url = /path/to/owncloud  # or https://domain.com/owncloud when using the REST API
    phpini = /path/to/custom/php.ini
    apilevel = v1-2  # or v2 for News 9.0.0 or greater
    mode = endless

Then run the updater with::

    owncloud-news-updater -c /path/to/config


**Note**: Command line parameters will always overwrite config parameters, so if you just want to change your loglevel to info for one run you can now do the following without globally changing the config file::

    owncloud-news-updater -c /path/to/config --testrun --loglevel info

Running The Updater As Systemd Service
--------------------------------------
Almost always you want to run and stop the updater using your in init system.
As for Systemd, you can create a simple text file at
**/etc/systemd/system/owncloud-news-updater.service** with the following contents:

.. code:: ini

    [Unit]
    After=default.target

    [Service]
    Type=simple
    User=http
    ExecStart=/usr/bin/owncloud-news-updater -c /etc/owncloud/news/updater.ini

    [Install]
    WantedBy=default.target

Then to enable and start it run::

    sudo systemctl enable owncloud-news-updater.service
    sudo systemctl start owncloud-news-updater.service

**Note**: If you are using the cli based updater (as in set an absolute directory as url)
you need to set the webserver user as user in the unit file. Otherwise the command
will fail because ownCloud checks for the owner of its files. This user
varies from distribution to distribution, e.g in Debian and Ubuntu you would use the
**www-data** user:

.. code:: ini

    [Unit]
    After=default.target

    [Service]
    Type=simple
    User=www-data
    ExecStart=/usr/bin/owncloud-news-updater -c /etc/owncloud/news/updater.ini

    [Install]
    WantedBy=default.target

If you are using the REST API, most of the time you can get away by using **nobody** as
user, but again, that might vary depending on your distribution.

Troubleshooting
----------------
If you are having trouble debugging updater errors, try running it again using the **info** loglevel::

    owncloud-news-updater --loglevel info -c /path/to/config.ini

How Do I Enable Support For Self-Signed Certificates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you are using self-signed certificates, don't. It's very easy to sign your cert for free from either one of the following three websites:

* `Lets Encrypt <https://letsencrypt.org/>`_
* `StartSSL <https://www.startssl.com/>`_
* `WoSign <https://www.wosign.com/english/>`_

If you still have to use a self-signed certificate no matter what, don't patch the code to turn off certificate verification but rather globally add your certificate to the trusted certificates. Read up on your distributions documentation to find out how.

Can I Run The Updater Using Cron
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Yes, you can by using the **--mode singlerun** parameter which will exit after an update.

However it's your job to ensure, that the job will not be executed more than once at the same time. This **can take down your system and/or server** since each new updater will slow down the previous ones causing more updaters to be spawned.

If you can not ensure that the updater is run only one at a time use the default mode (**--mode endless**). This mode runs the update in a loop. You can control the update frequency through the **--interval** parameter (or **interval** using a config file). The updater works in the following way:
* If a full update takes longer than the passed interval, another update will be run immediately afterwards
* If a full update took less than the passed interval, the updater will sleep for the remaining time and run an update afterwards


Using The CLI Based Updater Fails
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The updater uses the PHP executable to run the occ file inside your owncloud directory. The general process boils down to the following:

.. code-block:: bash

    # delete folders and feeds marked for deletion
    php -f /home/bernhard/programming/core/occ news:updater:before-update

    # get all feeds to udpate
    php -f /home/bernhard/programming/core/occ news:updater:all-feeds

    # run all feed updates
    php -f /home/bernhard/programming/core/occ news:updater:update-feed FEED_ID USER_ID

    # delete old articles
    php -f /home/bernhard/programming/core/occ news:updater:after-update

Most of the time there are two possible points of failure that can be debugged by using the **--logelevel info** parameter:


* Most distributions uses different **php.ini** files for your command line and web-server. This can manifest itself in weird errors like not being able to connect to the database. The solution is to either adjust **php.ini** used for the CLI PHP or to use a different **php.ini** altogether by specifying the **--phpini** parameter, e.g.::

    owncloud-news-updater -c /path/to/config --phpini /etc/php/owncloud-news-updater.ini

* The **news:updater:all-feeds** command returns invalid JSON. This can be due to due broken or missing **php.ini** settings or PHP warnings/errors produced by ownCloud. The solution to this issue can range from adjusting your **php.ini** (see previous point) to manually patching ownCloud to remove the warnings from the output.