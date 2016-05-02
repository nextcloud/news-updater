.. :changelog:

Changelog
---------

8.5.0
+++++

**Improvements**

- Command line parameters will now override config parameters in case both are present

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