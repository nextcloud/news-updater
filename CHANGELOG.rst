.. :changelog:

Changelog
---------

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