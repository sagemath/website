.PHONY: publications render clean show server style test cont

default: render

clean:
	- cd www && find -P -delete

publications:
	$(MAKE) -C publications

render: clean publications
	python render.py

server:
	cd www && python -m SimpleHTTPServer 8181

show:
	xdg-open http://127.0.0.1:8181/

open:
	python -c 'from webbrowser import open; open("./www/index.html")'

style:
	autopep8 -i -aaa -j -1 --ignore=E501 *.py scripts/*.py conf/*.py

test:
	python -m unittest discover

cont:
	python cont.py
