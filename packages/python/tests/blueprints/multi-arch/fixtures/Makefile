fake-target:
	echo 'here to make sure this file is modified'

# START: M-DOCKER-IMAGES
m-blueprints:
	m ci blueprints

dev-m-image1:
	packages/python/tests/blueprints/multi-arch/m/.m/blueprints/local/m-image1.build.sh

dev-m-image2: dev-m-image1
	packages/python/tests/blueprints/multi-arch/m/.m/blueprints/local/m-image2.build.sh

# END: M-DOCKER-IMAGES
