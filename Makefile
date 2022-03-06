image:
	docker build -t pyenv -f m/scripts/checks/Dockerfile

ciChecks:
	m/scripts/checks/run.sh ci

tests:
	m/scripts/checks/run.sh tests

shell:
	m/scripts/checks/shell.sh

bashTest:
	cd packages/bash/tests && ./run.sh
