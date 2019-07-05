dev:
	jupyter notebook &
	twistd -n web -p 'tcp:port=8000' --path ./docs &

gen:
	jupyter nbconvert docs/*.ipynb

kill:
	pkill twistd
	pkill jupyter

.PHONY: dev gen kill gen
