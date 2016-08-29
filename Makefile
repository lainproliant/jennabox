OUTPUT=build
ASSETS_IN=assets
ASSETS_OUT=$(OUTPUT)/static
LESSC=lessc

all: copy-code copy-font-awesome copy-minimal-css copy-jennabox-assets compile-jennabox-less

copy-code:
	mkdir -p $(OUTPUT)
	cp -r jennabox $(OUTPUT)/jennabox

copy-font-awesome:
	mkdir -p $(ASSETS_OUT)/font-awesome
	cp -r $(ASSETS_IN)/font-awesome/css $(ASSETS_OUT)/font-awesome/css
	cp -r $(ASSETS_IN)/font-awesome/fonts $(ASSETS_OUT)/font-awesome/fonts

copy-minimal-css:
	mkdir -p $(ASSETS_OUT)/css
	cp -r $(ASSETS_IN)/minimal-css/minimal.css $(ASSETS_OUT)/css/minimal.css

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

test: all
	cp test_run.py $(OUTPUT)
	pushd $(OUTPUT); pudb3 test_run.py; popd; rm -rf $(OUTPUT)
