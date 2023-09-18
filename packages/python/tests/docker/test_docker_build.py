from textwrap import dedent

import pytest
from m.docker.docker_build import DockerBuild
from pydantic import BaseModel


class TCase(BaseModel):
    id: str
    cmd: DockerBuild
    expected: str


@pytest.mark.parametrize(
    'tcase',
    [
        TCase(
            id='no_args',
            cmd=DockerBuild(tag=['tag1', 'tag2'], force_rm=True),
            expected="""\
                docker build \\
                  --force-rm \\
                  --tag tag1 \\
                  --tag tag2 \\
                  .""",
        ),
    ],
    ids=lambda tcase: tcase.id,
)
def test_docker_build(tcase: TCase) -> None:
    assert str(tcase.cmd) == dedent(tcase.expected)
