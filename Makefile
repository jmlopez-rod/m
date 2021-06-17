image:
	docker build -t pyenv -f build/Dockerfile

checks:
	docker run \
		--rm \
		-v "${PWD}":/checkout:z \
		-w /checkout \
		pyenv \
		/checkout/build/build.sh
