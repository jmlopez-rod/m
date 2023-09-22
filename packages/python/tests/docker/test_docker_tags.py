import pytest
from m.ci.docker.tags import docker_tags
from pydantic import BaseModel


class TCase(BaseModel):
    m_tag: str
    expected: list[str]


@pytest.mark.parametrize(
    'tcase',
    [
        TCase(m_tag=m_tag, expected=expected)
        for m_tag, expected in [
            ('0.0.1', ['latest', 'v0', 'v0.0']),
            ('1.22.333', ['latest', 'v1', 'v1.22']),
            ('99.999.9999', ['latest', 'v99', 'v99.999']),
            ('0.0.1-pr123.b12345', ['pr123']),
            ('0.0.1-rc123.b12345', ['next', 'pr123']),
            ('10.0.0-rc123.b12345', ['next', 'pr123']),
            ('0.100.0-rc123.b12345', ['next', 'pr123']),
            ('0.0.1000-rc123.b12345', ['next', 'pr123']),
            ('0.0.1-hotfix123.b12345', ['next', 'pr123']),
            ('10.0.0-hotfix123.b12345', ['next', 'pr123']),
            ('0.100.0-hotfix123.b12345', ['next', 'pr123']),
            ('0.0.1000-hotfix123.b12345', ['next', 'pr123']),
            ('99.999.9999-hotfix123.b12345', ['next', 'pr123']),
            ('0.0.1-master.b12345', ['master']),
            ('0.0.1-develop.b12345', ['develop']),
            ('0.0.1-branch.b12345', ['branch']),
        ]
    ],
    ids=lambda tcase: tcase.m_tag,
)
def test_docker_tags(tcase: TCase) -> None:
    assert docker_tags(tcase.m_tag) == tcase.expected
