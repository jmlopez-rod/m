fake-target:
	echo 'here to make sure this file is modified'

# START: M-DOCKER-IMAGES
define m_env
	$(eval include packages/python/tests/blueprints/single-arch/m/.m/m_env.sh)
	$(eval $(cut -d= -f1 packages/python/tests/blueprints/single-arch/m/.m/m_env.sh))
endef

m-env:
	mkdir -p packages/python/tests/blueprints/single-arch/m/.m && m ci env --bashrc > packages/python/tests/blueprints/single-arch/m/.m/m_env.sh

m-blueprints: m-env
	$(call m_env)
	m blueprints --skip-makefile --skip-workflow packages/python/tests/blueprints/single-arch/m
	chmod +x packages/python/tests/blueprints/single-arch/m/.m/blueprints/local/*.sh

dev-m-image1: m-blueprints
	$(call m_env)
	packages/python/tests/blueprints/single-arch/m/.m/blueprints/local/m-image1.build.sh

dev-m-image2: dev-m-image1
	$(call m_env)
	packages/python/tests/blueprints/single-arch/m/.m/blueprints/local/m-image2.build.sh

# END: M-DOCKER-IMAGES

other-target:
	echo 'showing that other targets are not overwritten'
