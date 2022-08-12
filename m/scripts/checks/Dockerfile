FROM python:3.8.7-alpine

RUN apk update && apk add bash

RUN pip install pycodestyle pydantic pylint mypy pyyaml wemake-python-styleguide flake8 pyformat isort add-trailing-comma coverage bandit==1.7.2
