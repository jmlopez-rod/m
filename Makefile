ci-checks:
	m/scripts/checks/ci.sh

tests:
	packages/python/tests/run.sh

mypy:
	mypy packages/python/m & mypy packages/python/tests & mypy packages/web/docs && mypy packages/web/hooks

localBuild:
	m/scripts/build.sh

devDocs:
	cd packages/web && mkdocs serve

deployDocs:
	cd packages/web && mkdocs gh-deploy

fix:
	pnpm exec prettier -w .

flake8:
	m/scripts/checks/flake8.sh

## Manual docker maintenance

buildUvDevContainer:
	IMAGE=uv-devcontainer m/bash/build.sh

buildPy311DevContainer:
	IMAGE=py311-devcontainer m/bash/build.sh

buildPy310DevContainer:
	IMAGE=py310-devcontainer m/bash/build.sh

publishPy311DevContainer: buildPy311DevContainer
	PY_VER=311 m/bash/publish.sh

publishPy310DevContainer: buildPy310DevContainer
	PY_VER=310 m/bash/publish.sh
