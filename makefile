.PHONY: publications render devmap clean show server style test cont mirrors

ARGS ?= ""

MIRROR_FILES := scripts/mirror_list scripts/metalink.helper scripts/torrent.helper templates/all-mirrors.html templates/mirrorselector-src.html templates/mirrorselector.html

default: clean render

clean:
	- mkdir -p www && cd www && find . -depth -mindepth 1 -delete

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
	cd www && python3 -m http.server 8181

show:
	python -c 'from webbrowser import open; open("http://127.0.0.1:8181/")'

open:
	python -c 'from webbrowser import open; open("./www/index.html")'

update:
	git checkout master
	git pull --ff-only
	git submodule foreach "git checkout master; git pull --ff-only origin master"

style:
	autopep8 -i -aaa -j -1 --ignore=E501 *.py scripts/*.py conf/*.py

test:
	python -m unittest discover

cont:
	python cont.py

publish: default
	bash publish.sh

pullpub:
	cd publications && git pull --ff-only && cd .. && git add publications && git commit -m "update publications" && git push

updpub: pullpub publish
