dev: jupyter_dev
dev: web_dev

jupyter_dev:
	jupyter notebook &

web_dev:
	twistd -n web -p 'tcp:port=8000' --path ./ &

web_gen:
	jupyter nbconvert *.ipynb

dockill:
	pkill twistd
	pkill jupyter

.PHONY: docdev docgen dockill
