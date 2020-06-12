dev:
	jupyter notebook ./docs &
	twistd -n web -p 'tcp:port=8000' --path ./docs &

gen:
	cd docs && jupyter nbconvert *.ipynb

kill:
	pkill twistd
	pkill jupyter

black:
	black wlpac/*.py

.PHONY: dev gen kill gen
