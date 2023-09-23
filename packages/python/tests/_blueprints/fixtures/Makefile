fake-target:
	echo 'here to make sure this file is modified'

# START: M-DOCKER-IMAGES
m-blueprints:
	m ci blueprints

dev-m-image1:
	packages/python/tests/_blueprints/m_dir/.m/blueprints/local/m-image1__build.sh

dev-m-image2: dev-m-image1
	packages/python/tests/_blueprints/m_dir/.m/blueprints/local/m-image2__build.sh

# END: M-DOCKER-IMAGES
