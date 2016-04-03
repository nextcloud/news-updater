# This makefile is only intended for development

install:
	sudo python3 setup.py install --install-scripts=/usr/bin

clean:
	rm -rf dist
	rm -rf MANIFEST
	rm -rf build
	rm -rf owncloud_news_updater.egg-info

update: clean
	sudo pip3 uninstall owncloud_news_updater
	sudo python3 setup.py install

uninstall: clean
	sudo pip3 uninstall owncloud_news_updater

pypi: clean
	python3 setup.py sdist upload