ci-checks:
	m/scripts/checks/ci.sh

tests:
	packages/python/tests/run.sh

fmt:
	deno fmt

mypy:
	mypy packages/python/m & mypy packages/python/tests

localBuild:
	m/scripts/build.sh

devDocs:
	cd packages/website && pnpm start

deployDocs:
	cd packages/website && USE_SSH=true npm run deploy

fix:
	pnpm exec prettier -w .

## Manual docker maintenance

buildPy311DevContainer:
	IMAGE=py311-devcontainer m/bash/build.sh

buildPy310DevContainer:
	IMAGE=py310-devcontainer m/bash/build.sh

publishPy311DevContainer: buildPy311DevContainer
	PY_VER=311 m/bash/publish.sh

publishPy310DevContainer: buildPy310DevContainer
	PY_VER=310 m/bash/publish.sh

