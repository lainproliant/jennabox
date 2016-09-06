OUTPUT=build
ASSETS_IN=assets
ASSETS_OUT=$(OUTPUT)/static
LESSC=lessc

all: copy-code copy-font-awesome copy-bootstrap copy-jennabox-assets compile-jennabox-less

copy-code:
	mkdir -p $(OUTPUT)
	cp -r jennabox $(OUTPUT)/jennabox
	cp logging.ini $(OUTPUT)/
	cp jennabox-ddl.sql $(OUTPUT)/

copy-font-awesome:
	mkdir -p $(ASSETS_OUT)/font-awesome
	cp -r $(ASSETS_IN)/font-awesome/css $(ASSETS_OUT)/font-awesome/css
	cp -r $(ASSETS_IN)/font-awesome/fonts $(ASSETS_OUT)/font-awesome/fonts

copy-bootstrap:
	cp -r $(ASSETS_IN)/bootstrap/dist $(ASSETS_OUT)/bootstrap

copy-jennabox-assets:
	mkdir -p $(ASSETS_OUT)/js $(ASSETS_OUT)/images
	cp -r $(ASSETS_IN)/js/*.js $(ASSETS_OUT)/js
	cp -r $(ASSETS_IN)/images/* $(ASSETS_OUT)/images

compile-jennabox-less:
	mkdir -p $(ASSETS_OUT)/css
	python compile-less.py

server: all
	cd $(OUTPUT); python -m jennabox.server

clean:
	rm -rf $(OUTPUT)

debug: all
	cp test_run.py $(OUTPUT)
	pushd $(OUTPUT); pudb3 test_run.py; popd; rm -rf $(OUTPUT)

test: all
	cp test_run.py $(OUTPUT)
	pushd $(OUTPUT); python test_run.py; popd; rm -rf $(OUTPUT)
