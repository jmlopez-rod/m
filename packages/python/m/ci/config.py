from dataclasses import dataclass
from ..core.fp import OneOf, one_of
from ..core.json import read_json, multi_get
from ..core.issue import Issue


@dataclass
class Config:
    """Object to store the m project configuration."""
    owner: str
    repo: str
    version: str
    m_dir: str


def read_config(m_dir: str) -> OneOf[Issue, Config]:
    """Read an m configuration file."""
    return one_of(lambda: [
        Config(owner, repo, version, m_dir)
        for data in read_json(f'{m_dir}/m.json')
        for owner, repo, version in multi_get(data, 'owner', 'repo', 'version')
    ])
