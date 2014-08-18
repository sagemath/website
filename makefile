.PHONY: render clean show server

render:
	python render.py

server:
	cd www && python -m SimpleHTTPServer 8181

show:
	xdg-open http://127.0.0.1:8181/

