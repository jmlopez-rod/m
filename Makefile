image:
	docker build -t pyenv -f build/Dockerfile

ciChecks:
	./build/run.sh build

pyTest:
	./build/run.sh tests

shell:
	./build/shell.sh

bashTest:
	cd packages/bash/tests && ./run.sh
