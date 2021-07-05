image:
	docker build -t pyenv -f build/Dockerfile

checks:
	./build/run.sh build

pyTest:
	./build/run.sh tests

bashTest:
	cd packages/bash/tests && ./run.sh
