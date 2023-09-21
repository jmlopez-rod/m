from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .filenames import FileNames
from .image import DockerImage


def to_kebab(snake: str) -> str:
    """Convert snake case to kebab case.

    Args:
        snake: The string to convert.

    Returns:
        The converted string in kebab-case.
    """
    return snake.replace('_', '-', -1)


class Step(BaseModel):
    """Representation of a Github job step."""

    model_config = ConfigDict(
        extra='allow',
        populate_by_name=True,
    )

    name: str | None = None

    id: str | None = None

    uses: str | None = None

    action_options: dict[str, Any] | None = Field(default=None, alias='with')

    run: str | None = None


class Strategy(BaseModel):
    """Representation of a Github job strategy."""

    model_config = ConfigDict(alias_generator=to_kebab, extra='allow')

    # https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs
    # will use with `include` to specify an array of values.
    matrix: dict[str, Any]

    fail_fast: bool | None = None

    @classmethod
    def create(
        cls: type['Strategy'],
        architectures: dict[str, str | list[str]],
    ) -> 'Strategy':
        """Create an instance of Strategy.

        Args:
            architectures: The architectures to use.

        Returns:
            An instance of Strategy.
        """
        return Strategy(
            fail_fast=False,
            matrix={
                'include': [
                    {'arch': arch, 'os': os}
                    for arch, os in architectures.items()
                ],
            },
        )


class Job(BaseModel):
    """Representation of a Github job."""

    model_config = ConfigDict(
        alias_generator=to_kebab,
        extra='allow',
        populate_by_name=True,
    )

    runs_on: str | list[str]

    needs: str | list[str] | None = None

    strategy: Strategy | None = None

    env: dict[str, str] | None = None

    outputs: dict[str, str] | None = None

    steps: list[Step]

    @classmethod
    def create(
        cls: type['Job'],
        architectures: dict[str, str | list[str]],
    ) -> 'Job':
        """Create an instance of Job.

        Args:
            name: The name of the job.
            architectures: The architectures to use.

        Returns:
            An instance of Job.
        """
        return Job(
            strategy=Strategy.create(architectures),
            runs_on='${{ matrix.os }}',
            steps=[],
        )

    def update(
        self: 'Job',
        architectures: dict[str, str | list[str]],
    ) -> None:
        """Update the job.

        Args:
            architectures: The architectures to use.
        """
        self.runs_on = '${{ matrix.os }}'
        self.strategy = Strategy.create(architectures)
        self.steps = []


class Workflow(BaseModel):
    """Representation of a Github workflow."""

    model_config = ConfigDict(alias_generator=to_kebab, extra='allow')

    name: str

    on: dict[str, Any]

    jobs: dict[str, Job]

    def update_build_job(
        self: 'Workflow',
        architectures: dict[str, str | list[str]],
        images: list[DockerImage],
        files: FileNames,
    ) -> None:
        """Update the build job.

        Args:
            architectures: The architectures to use.
            images: The DockerImage instances.
            files: The FileNames instance with the file names.
        """
        self.jobs = self.jobs or {}
        # target reference to the job we will manage
        job = self.jobs.get('docker-build') or Job.create(architectures)
        self.jobs['docker-build'] = job
        job.runs_on = '${{ matrix.os }}'
        job.env = job.env or {}
        job.env['ARCH'] = '${{ matrix.arch }}'
        job.strategy = Strategy.create(architectures)
        # create steps
        job.steps = [
            Step(
                name='checkout',
                uses='actions/checkout@v4',
            ),
            Step(
                name='restore-m-blueprints',
                uses='actions/download-artifact@v3',
                action_options={
                    'name': 'm-blueprints',
                },
            ),
        ]
        job.needs = 'setup'
        for img in images:
            sub_steps = ['cache', 'build', 'push']
            for sub_step in sub_steps:
                job.steps.append(
                    Step(
                        name=f'{img.image_name} - {sub_step}',
                        run=files.ci_step(img.image_name, sub_step),
                    ),
                )

    def update_setup_job(self: 'Workflow') -> None:
        """Update the setup job."""
        self.jobs = self.jobs or {}
        yq_cmd = 'yq -o=json -I=0 m/.m/docker-images/ci/manifests.json'
        steps = [
            Step(
                name='checkout',
                uses='actions/checkout@v4',
            ),
            Step(
                name='install-m',
                run='pip install jmlopez-m',
            ),
            Step(
                name='blueprints',
                run='m ci blueprints',
            ),
            Step(
                name='output-manifests',
                id='manifests',
                run=f'{{\n  echo "manifests=$({yq_cmd})"\n}} >> $GITHUB_OUTPUT',
            ),
            Step(
                name='archive',
                uses='actions/upload-artifact@v3',
                action_options={
                    'name': 'm-blueprints',
                    'path': 'm/.m',
                },
            ),
        ]
        job = self.jobs.get('setup') or Job(
            runs_on='Ubuntu-22.04',
            steps=steps,
        )
        job.runs_on = 'Ubuntu-22.04'
        job.outputs = job.outputs or {}
        job.outputs['manifests'] = '${{ steps.manifests.outputs.manifests }}'
        job.steps = steps
        self.jobs['setup'] = job
