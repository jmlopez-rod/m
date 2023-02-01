ciChecks:
	m/scripts/checks/ci.sh

tests:
	packages/python/tests/run.sh

bashTest:
	cd packages/bash/tests && ./run.sh

localPublish:
	m/scripts/publish.sh

devDocs:
	cd packages/website && pnpm start

deployDocs:
	cd packages/website && USE_SSH=true pnpm deploy

## Manual docker maintenance

buildDevContainer:
	m/bash/build.sh

publishDevContainer:
	m/bash/publish.sh
