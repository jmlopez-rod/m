from functools import partial
from typing import Callable

from m.core import Bad, Good, Res, issue, one_of, yaml
from m.core.rw import insert_to_file, write_file
from m.pydantic import load_model
from pydantic import BaseModel

from .env import MEnvDocker
from .filenames import FileNames
from .gh_workflow import Workflow
from .image import DockerImage


class DockerConfig(BaseModel):
    """Contains information about the docker images to build."""

    # A map of the architectures to build. It maps say `amd64` to a Github
    # runner that will build the image for that architecture.
    #   amd64: Ubuntu 20.04
    architectures: dict[str, str]

    # Base path used to locate docker files. Defaults to `.` (root of project)
    # but may be changed a specific directory.
    base_path: str = '.'

    # Name of the docker registry to push the images to.
    docker_registry: str

    # list of images to build
    images: list[DockerImage]

    def makefile_targets(self: 'DockerConfig', files: FileNames) -> str:
        """Create the Makefile targets to trigger the local builds.

        Args:
            files: Instance of FileNames to obtain the names of the scripts.

        Returns:
            A string with the Makefile targets.
        """
        lines: list[str] = [
            'm-blueprints:',
            '\tm ci blueprints\n',
        ]
        for index, img in enumerate(self.images):
            name = img.image_name
            img_file = files.local_step(name)
            previous_img = (
                self.images[index - 1].image_name
                if index > 0
                else None
            )
            # Should it call `m-blueprints` as dependency?
            dep = f' dev-{previous_img}' if previous_img else ''
            lines.append(f'dev-{name}:{dep}')
            lines.append(f'\t{img_file}\n')
        return '\n'.join(lines)

    def update_makefile(self: 'DockerConfig', files: FileNames) -> Res[None]:
        """Update the Makefile with the docker images targets.

        Args:
            files: Instance of FileNames to obtain the names of the scripts.

        Returns:
            None if successful, else an issue.
        """
        return insert_to_file(
            files.makefile,
            '\n# START: M-DOCKER-IMAGES\n',
            self.makefile_targets(files),
            '\n# END: M-DOCKER-IMAGES\n',
        )

    def update_github_workflow(
        self: 'DockerConfig',
        files: FileNames,
    ) -> Res[None]:
        """Update the github workflow with the docker images targets.

        Args:
            files: Instance of FileNames to obtain the names of the scripts.

        Returns:
            None if successful, else an issue.
        """
        model_res = load_model(Workflow, files.gh_workflow)
        if isinstance(model_res, Bad):
            return issue(
                'update_github_workflow_failure',
                context={'issue': model_res.value.to_dict(show_traceback=False)},
            )
        obj = model_res.value.model_dump(by_alias=True)
        print(yaml.dumps(obj, sort_keys=False))
        return Good(None)

    def write_local_step(
        self: 'DockerConfig',
        files: FileNames,
        img: DockerImage,
        m_env: MEnvDocker,
    ) -> Res[None]:
        """Write a local build step for an image.

        Args:
            files: The FileNames instance with the file names.
            img: The DockerImage instance.
            m_env: The MEnvDocker instance with the environment variables.

        Returns:
            None if successful, else an issue.
        """
        file_name = files.local_step(img.image_name)
        return one_of(lambda: [
            None
            for script_content in img.local_build(m_env)
            for _ in write_file(file_name, script_content)
        ])

    def write_local_steps(
        self: 'DockerConfig',
        files: FileNames,
        m_env: MEnvDocker,
    ) -> Res[None]:
        """Write local entry point files.

        Args:
            files: The FileNames instance with the file names.
            m_env: The MEnvDocker instance with the environment variables.

        Returns:
            None if successful, else an issue.
        """
        issues: list[dict] = []
        for img in self.images:
            write_res = self.write_local_step(files, img, m_env)
            if isinstance(write_res, Bad):
                dict_issue = write_res.value.to_dict(show_traceback=False)
                issues.append(dict(dict_issue))
        if issues:
            return issue(
                'write_local_steps_failure',
                context={'issues': issues},
            )
        return Good(None)

    def write_ci_step(
        self: 'DockerConfig',
        files: FileNames,
        img: DockerImage,
        step_name: str,
        callback: Callable[[], Res[str]],
    ) -> Res[None]:
        """Write a ci step for an image.

        Args:
            files: The FileNames instance with the file names.
            img: The DockerImage instance.
            step_name: The step name used in generating the image.
            callback: The callback that generate the script content.

        Returns:
            None if successful, else an issue.
        """
        file_name = files.ci_step(img.image_name, step_name)
        return one_of(lambda: [
            None
            for script_content in callback()
            for _ in write_file(file_name, script_content)
        ])

    def write_ci_steps(
        self: 'DockerConfig',
        files: FileNames,
        m_env: MEnvDocker,
    ) -> Res[None]:
        """Write ci entry point files.

        Args:
            files: The FileNames instance with the file names.
            m_env: The MEnvDocker instance with the environment variables.

        Returns:
            None if successful, else an issue.
        """
        issues: list[dict] = []
        for img in self.images:
            steps_res = [
                self.write_ci_step(files, img, step_name, callback)
                for step_name, callback in (
                    ('build', partial(img.ci_build, m_env)),
                    ('cache', partial(img.ci_cache, m_env)),
                )
            ]
            for step_res in steps_res:
                if isinstance(step_res, Bad):
                    dict_issue = step_res.value.to_dict(show_traceback=False)
                    issues.append(dict(dict_issue))
        if issues:
            return issue(
                'write_ci_steps_failure',
                context={'issues': issues},
            )
        return Good(None)

    def write_blueprints(
        self: 'DockerConfig',
        m_dir: str,
        m_env: MEnvDocker,
    ) -> Res[None]:
        """Write entry point files.

        Writes shell files for both local and ci. Updates the Makefile and
        github workflow file.

        Args:
            m_dir: The m directory.
            m_env: The MEnvDocker instance with the environment variables.

        Returns:
            None if successful, else an issue.
        """
        files = FileNames.create_instance(m_dir)
        return one_of(lambda: [
            None
            for _ in self.update_makefile(files)
            for _ in self.update_github_workflow(files)
            for _ in self.write_local_steps(files, m_env)
            for _ in self.write_ci_steps(files, m_env)
        ])
