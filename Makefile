ci-checks:
	m/scripts/checks/ci.sh

tests:
	packages/python/tests/run.sh

mypy:
	mypy packages/python/m & mypy packages/python/tests

localPublish:
	m/scripts/publish.sh

devDocs:
	cd packages/website && pnpm start

deployDocs:
	cd packages/website && USE_SSH=true npm run deploy

## Manual docker maintenance

buildPy311DevContainer:
	IMAGE=py311-devcontainer m/bash/build.sh

buildPy310DevContainer:
	IMAGE=py310-devcontainer m/bash/build.sh

publishPy311DevContainer: buildPy311DevContainer
	PY_VER=311 m/bash/publish.sh

publishPy310DevContainer: buildPy310DevContainer
	PY_VER=310 m/bash/publish.sh

