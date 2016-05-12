.. :changelog:

Changelog
---------

9.0.1
+++++

**Bugfixes**

- Fix bug that would prevent running the updater on some systems, #4

9.0.0
+++++

**Breaking Changes**

* Require Python 3.4 or greater
* Config files are now validated. Unknown config keys will throw an error and abort the updater
* The **--testrun** command line argument was removed in order to officially support starting the updater using your cron. Use **--mode singlerun** instead

**Bugfixes**

- Fix bug that would exit update in singlerun mode when an error occurred during update
- Fix bug that would not run the after cleanup command in cli mode and would therefore never remove old articles

**Improvements**

* Added a **--mode** parameter which allows you to run the updater using a cron. You have to ensure that only one instance run at a time however (e.g. using SystemD timers)
* Added automated tests which cover the full functionality

8.5.0
+++++

**Improvements**

- Command line parameters will now override config parameters in case both are present
- Remove **testrun** from allowed config parameters

**Bugfixes**

- Fix bug that would not parse integer and boolean values in config file properly

8.4.0
+++++

**Improvements**

- Add a console and config parameter for setting a custom php.ini path
- Add support for API v2 which is in draft phase

8.3.1
+++++

**Bugfixes**

- Get rid of the requirements.txt missing warning when install the lib
- If a JSON parsing error happens, create a more helpful error message

8.3.0
+++++

**Improvements**

- Get rid of the python-requests dependency. The library now needs zero dependencies and can be used very easily.

8.2.6
+++++

**Miscellaneous**

- Move the updater from the News repository into a separate one
- Publish the app on pypi so it can be installed using pip
- Require Python 3.2 as minimum Python version
- Remove outdated rpm installation script
- Remove platform dependant Makefile commands, use setuptools directly
- Remove outdated rpm spec file
- Remove platform dependant systemd unit file, since it varies too much depending on the distribution. Instead describe how to create a unit file in the README.rst