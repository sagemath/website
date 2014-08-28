.PHONY: publications render devmap clean show server style test cont

ARGS ?= ""

default: render

clean:
	- cd www && find -P -delete

devmap: templates/devs.html

templates/devs.html: scripts/geocode.xml scripts/geocode.py scripts/contributors.xml
	python scripts/geocode.py

publications:
	$(MAKE) -C publications

render: clean publications devmap
	python render.py $(ARGS)

server:
	cd www && python -m SimpleHTTPServer 8181

show:
	python -c 'from webbrowser import open; open("http://127.0.0.1:8181/")'

open:
	python -c 'from webbrowser import open; open("./www/index.html")'

style:
	autopep8 -i -aaa -j -1 --ignore=E501 *.py scripts/*.py conf/*.py

test:
	python -m unittest discover

cont:
	python cont.py
