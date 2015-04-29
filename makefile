.PHONY: publications render devmap clean show server style test cont mirrors

ARGS ?= ""

MIRROR_FILES := scripts/mirror_list scripts/metalink.helper scripts/torrent.helper templates/all-mirrors.html templates/mirrorselector-src.html templates/mirrorselector.html

default: render

clean:
	- cd www && find -P -delete

devmap: templates/devs.html

templates/devs.html: conf/geocode.xml scripts/geocode.py conf/contributors.xml
	python scripts/geocode.py

mirrors: $(MIRROR_FILES)

$(MIRROR_FILES): scripts/mirror_manager.py conf/mirrors.yaml
	bash scripts/mirror_manager_wrapper.sh


publications:
	$(MAKE) -C publications

render: mirrors publications devmap
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
