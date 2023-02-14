import logging
from dataclasses import dataclass
from typing import Callable

from m.core import Issue, OneOf
from pydantic import BaseModel, Field


class EnvVars(BaseModel):
    """Class to store the values of the environment variables."""

    # pylint: disable=too-many-instance-attributes
    ci_env: bool = False
    github_token: str = ''
    server_url: str = ''
    run_id: str = ''
    run_number: str = ''
    run_url: str = ''
    git_branch: str = ''
    git_sha: str = ''
    triggered_by: str = ''
    triggered_by_email: str = ''
    triggered_by_user: str = ''


class Message(BaseModel):
    """Parameters needed to deliver a warning or error message."""

    msg: str = Field(description='message to display')
    title: str | None = Field(default=None, description='custom title')
    file: str | None = Field(  # noqa: WPS110 - required by Github
        default=None,
        description='filename',
    )
    line: str | None = Field(
        default=None,
        description='line number, starting at 1',
    )
    end_line: str | None = Field(default=None, description='end line number')
    col: str | None = Field(
        default=None,
        description='column number, starting at 1',
    )
    end_col: str | None = Field(default=None, description='end column number')

    class Config:
        """Allow other types."""

        arbitrary_types_allowed = True


@dataclass
class ProviderModule:
    """Container to store functions from the providers."""

    ci: bool
    env_vars: Callable[[], OneOf[Issue, EnvVars]]
    formatter: Callable[
        [logging.Formatter, logging.LogRecord, bool, bool],
        str,
    ]
