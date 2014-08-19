.PHONY: render clean show server

default: render

clean:
	- rm -rf www
	- mkdir www

render: clean
	python render.py

server:
	cd www && python -m SimpleHTTPServer 8181

show:
	xdg-open http://127.0.0.1:8181/

