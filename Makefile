SHELL=/bin/bash

ci-checks:
	m/scripts/checks/ci.sh

tests:
	packages/python/tests/run.sh

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

pylint:
	m/scripts/checks/pylint.sh

## Manual docker maintenance

buildPy311DevContainer:
	IMAGE=py311-devcontainer m/bash/build.sh

buildPy310DevContainer:
	IMAGE=py310-devcontainer m/bash/build.sh

publishPy311DevContainer: buildPy311DevContainer
	PY_VER=311 m/bash/publish.sh

publishPy310DevContainer: buildPy310DevContainer
	PY_VER=310 m/bash/publish.sh

# START: M-DOCKER-IMAGES
m-blueprints:
	mkkdir -m
	m ci blueprints

dev-m-image1:
	m/.m/blueprints/local/m-image1.build.sh

dev-m-image2: dev-m-image1
	m/.m/blueprints/local/m-image2.build.sh

# END: M-DOCKER-IMAGES

define m_env
	$(eval include tmp.sh)
	$(eval $(cut -d= -f1 tmp.sh))
endef

create-env:
	echo 'export T1=abcA2' > tmp.sh
	echo 'export T2=defB2' >> tmp.sh

create: create-env
	$(call m_env)
	echo "on create ${T1} - ${T2}"

t2: create
	$(call m_env)
	echo "on t2: ${T1} - ${T2}"

t3: t2
	$(call m_env)
	echo "on t3: ${T1} - ${T2}"
