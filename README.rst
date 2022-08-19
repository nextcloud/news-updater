Nextcloud News Updater
======================

.. image:: https://img.shields.io/pypi/v/nextcloud_news_updater.svg
    :target: https://pypi.python.org/pypi/nextcloud_news_updater
.. image:: https://travis-ci.org/nextcloud/news-updater.svg?branch=master
    :target: https://travis-ci.org/nextcloud/news-updater

This Python library is a parallel feed updater for the `Nextcloud News app <https://github.com/nextcloud/news>`_


Nextcloud does not require people to install threading or multiprocessing
libraries. Because the feed update process is mainly limited by I/O, parallel
fetching of RSS feed updates can speed up the updating process significantly.

In addition, Web Cron is not a supported cron setting since the update
process may time out.

Therefore the News app provides an API that offers a more fine grained
control over updating feeds. This Python project implements an update
mechanism that is based on the `updater REST API <https://github.com/nextcloud/news/tree/master/docs>`_ or (new in Nextcloud News 8.1.0) the
console based update API.

.. contents:: :local:

Dependencies
------------

* **Python >=3.5**

Pre-Installation
----------------

To run the updates via an external threaded script the cron updater has to be
disabled. To do that go to the admin section an uncheck the **Use Nextcloud
cron** checkbox or open **nextcloud/data/news/config/config.ini** and set::

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
documentation <http://python-packaging-user-guide.readthedocs.org/en/latest/install_requirements_linux/>`_

**Note**: You need to install the Python 3 version of pip

After installing pip, run::

    sudo pip3 install nextcloud_news_updater

To update the library, run::

    sudo pip3 install --upgrade nextcloud_news_updater

To uninstall the library run::

    sudo pip3 uninstall nextcloud_news_updater

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

    python3 -m nextcloud_news_updater /path/to/nextcloud

Usage
-----

There are two ways to run the updater:

* Using the console API (recommended)::

    nextcloud-news-updater /path/to/nextcloud

* Using the REST API (when running the updater on a different machine than Nextcloud)::

    nextcloud-news-updater https://domain.com/path/to/nextcloud --user admin_user --password admin_password

**Note**: **admin_user** is a user id with admin rights, **admin_password** the user's password

You can view all options by running::

    nextcloud-news-updater --help

::

    usage: __main__.py [-h] [--threads THREADS] [--timeout TIMEOUT]
                       [--interval INTERVAL] [--apilevel {v1-2,v2,v15}]
                       [--loglevel {info,error}] [--config CONFIG]
                       [--phpini PHPINI] [--user USER] [--password PASSWORD]
                       [--version] [--mode {endless,singlerun}] [--php PHP]
                       [url]

    positional arguments:
      url                   The URL or absolute path to the directory where
                            Nextcloud is installed. Must be specified on the
                            command line or in the config file. If the URL starts
                            with http:// or https://, a user and password are
                            required. Otherwise the updater tries to use the
                            console based API which was added in 8.1.0

    optional arguments:
      -h, --help            show this help message and exit
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
      --apilevel {v1-2,v2,v15}, -a {v1-2,v2,v15}
                            API level. Use v15 for News 15 or later, or v1-2 for
                            releases prior to that
      --loglevel {info,error}, -l {info,error}
                            Log granularity, info will log all urls and received
                            data, error will only log errors
      --config CONFIG, -c CONFIG
                            Path to config file where all parameters except can be
                            defined as key values pair. See the README.rst for 
                            more information
      --phpini PHPINI, -P PHPINI
                            Custom absolute path to the php.ini file to use for
                            the command line updater. If omitted, the default one
                            will be used
      --user USER, -u USER  Admin username to log into Nextcloud. Must be
                            specified on the command line or in the config file if
                            the updater should update over HTTP
      --password PASSWORD, -p PASSWORD
                            Admin password to log into Nextcloud if the updater
                            should update over HTTP
      --version, -v         Prints the updater's version
      --mode {endless,singlerun}, -m {endless,singlerun}
                            Mode to run the updater in: endless runs the update
                            again after the specified interval, singlerun only
                            executes the update once
      --php PHP             Path to the PHP binary, e.g. /usr/bin/php7.0, defaults
                            to php



You can also put your settings in a config file, looking like this:

.. code:: ini

    [updater]
    threads = 10
    interval = 900
    loglevel = error
    # or https://domain.com/nextcloud when using the REST API
    url = /path/to/nextcloud
    # or v2 which is currently a draft
    apilevel = v15
    mode = endless
    
    # The following lines are only needed when using the REST API
    user = admin
    password = admin

    # The following lines are only needed when using the console API 
    # path to php binary
    php = /usr/bin/php7.0
    phpini = /path/to/custom/php.ini

**Warning**: If you use REST API with user and password assigned in the config file, you probably don't want anyone else but the file owner to see your user/password in the file. Secure it with::

    chmod 600 /path/to/config

**Note**: You can omit options in the config file if you want to use the defaults, but you can not have more than the allowed parameters present, otherwise an exception will abort the updater.

Then run the updater with::

    nextcloud-news-updater -c /path/to/config


**Note**: Command line parameters will always overwrite config parameters, so if you just want to change your loglevel to info for one run you can now do the following without globally changing the config file::

    nextcloud-news-updater -c /path/to/config --mode singlerun --loglevel info

Running The Updater As Systemd Service
--------------------------------------
Almost always you want to run and stop the updater using your in init system.
As for Systemd, you can create a simple text file at
**/etc/systemd/system/nextcloud-news-updater.service** with the following contents:

.. code:: ini

    [Unit]
    After=default.target

    [Service]
    Type=simple
    User=http
    ExecStart=/usr/bin/nextcloud-news-updater -c /etc/nextcloud/news/updater.ini

    [Install]
    WantedBy=default.target

Then to enable and start it run::

    sudo systemctl enable nextcloud-news-updater.service
    sudo systemctl start nextcloud-news-updater.service

**Note**: If you are using the cli based updater (as in set an absolute directory as url)
you need to set the web-server user as user in the unit file. Otherwise the command
will fail because Nextcloud checks for the owner of its files. This user
varies from distribution to distribution, e.g in Debian and Ubuntu you would use the
**www-data** user:

.. code:: ini

    [Unit]
    After=default.target

    [Service]
    Type=simple
    User=www-data
    ExecStart=/usr/bin/nextcloud-news-updater -c /etc/nextcloud/news/updater.ini

    [Install]
    WantedBy=default.target

If you are using the REST API, most of the time you can get away by using **nobody** as
user, but again, that might vary depending on your distribution.

Running The Updater As OpenRC Service
--------------------------------------
On Alpine/postmarketOS/Gentoo/Artix or the other OpenRC based distros, you can create a simple text file at
**/etc/init.d/nextcloud-news-updater** with the following contents:

.. code:: sh
    
    #!/sbin/openrc-run

    description="Nextcloud News Updater Daemon"

    log_dir="/var/log/$RC_SVCNAME"
    pidfile=${pidfile:-/run/$RC_SVCNAME.pid}
    output_log="${output_log:-$log_dir/output.log}"
    error_log="${error_log:-$log_dir/error.log}"

    config_dir="/etc/$RC_SVCNAME"
    config_file="$config_dir/updater.ini"

    command=${command:-/usr/bin/nextcloud-news-updater}
    command_user=${command_user:-nextcloud:nextcloud}
    command_args="-c $config_file"
    command_background=true

    depend() {
            need net
            use mariadb postgresql
    }

    start_pre() {
    	checkpath --directory --owner $command_user "$log_dir"
    	checkpath --file --owner $command_user "$output_log" "$error_log"
    	checkpath --directory "$config_dir"
    	checkpath --file --mode 0600 --owner $command_user "$config_file"
    }

Then to enable and start it run::

    sudo chmod 755 /etc/init.d/nextcloud-news-updater
    sudo rc-update add nextcloud-news-updater
    sudo rc-service nextcloud-news-updater start

Troubleshooting
----------------
If you are having trouble debugging updater errors, try running it again using the **info** loglevel::

    nextcloud-news-updater --loglevel info -c /path/to/config.ini

How Do I Enable Support For Self-Signed Certificates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you are using self-signed certificates, don't. It's very easy to sign your cert for free from `Lets Encrypt <https://letsencrypt.org/>`_

If you still have to use a self-signed certificate no matter what, don't patch the code to turn off certificate verification but rather globally add your certificate to the trusted certificates. Read up on your distributions documentation to find out how.

Can I Run The Updater Using Cron
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Yes, you can by using the **--mode singlerun** parameter which will exit after one full update.

However it's your job to ensure, that the job will not be executed more than once at the same time. If update jobs overlap, they **can take down your system and/or server** since each new updater will slow down the previous ones causing more updaters to be spawned.

If you can not ensure that the updater is run only one at a time use the default mode (**--mode endless**). This mode runs the update in a loop. You can control the update frequency through the **--interval** parameter (or **interval** using a config file). The updater works in the following way:
* If a full update takes longer than the passed interval, another update will be run immediately afterwards
* If a full update took less than the passed interval, the updater will sleep for the remaining time and run an update afterwards


Using The CLI Based Updater Fails
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The updater uses the PHP executable to run the occ file inside your nextcloud directory. The general process boils down to the following:

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

    nextcloud-news-updater -c /path/to/config --phpini /etc/php/nextcloud-news-updater.ini

* The **news:updater:all-feeds** command returns invalid JSON. This can be due to due broken or missing **php.ini** settings or PHP warnings/errors produced by Nextcloud. The solution to this issue can range from adjusting your **php.ini** (see previous point) to manually patching Nextcloud to remove the warnings from the output.

Working with Centos/RHEL
~~~~~~~~~~~~~~~~~~~~~~~~
Since Centos only provides Python 3.4, you can use `SoftwareCollections <https://www.softwarecollections.org>`_ to install a newer Python version.

For example Python 3.5: https://www.softwarecollections.org/en/scls/rhscl/rh-python35/

.. code-block:: bash

    # 1. Install the Software Collection Repository
    $ sudo yum install centos-release-scl

    # 2. Install the collection:
    $ sudo yum install rh-python35

    # 3. Start using software collections:
    $ scl enable rh-python35 bash

    # 4. Install nextcloud-news.updater
    $ sudo pip3 install nextcloud_news_updater

After the install you can run the updater as a service by extending the service file with the correct environment variable for your Python version. In this example we use Python 3.5:

.. code:: ini

    [Unit]
    After=default.target

    [Service]
    Type=simple
    User=http
    ExecStart=/usr/bin/nextcloud-news-updater -c /etc/nextcloud-news-updater.ini
    Environment=LD_LIBRARY_PATH=/opt/rh/rh-python35/root/usr/lib64

    [Install]
    WantedBy=default.target
