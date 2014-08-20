.PHONY: publications render clean show server

default: render

clean:
	- cd www && find -P -delete

publications:
	cd publications && python pubparse.py

render: clean publications
	python render.py

server:
	cd www && python -m SimpleHTTPServer 8181

show:
	xdg-open http://127.0.0.1:8181/

open:
	python -c 'from webbrowser import open; open("./www/index.html")'
