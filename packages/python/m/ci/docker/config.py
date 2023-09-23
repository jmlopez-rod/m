import json
from functools import partial
from typing import Any, Callable

from m.core import Bad, Good, Res, issue, one_of
from m.core.rw import insert_to_file, write_file
from pydantic import BaseModel

from .env import MEnvDocker
from .filenames import FileNames
from .gh_workflow import Workflow
from .image import DockerImage
from .shell_scripts import create_cache_script, create_push_script


class DockerConfig(BaseModel):
    """Contains information about the docker images to build."""

    # default runner to use when creating blueprints and manifests
    default_runner: str = 'ubuntu-22.04'

    # A map of the architectures to build. It maps say `amd64` to a Github
    # runner that will build the image for that architecture.
    #   amd64: Ubuntu 20.04
    architectures: dict[str, str | list[str]]

    # Base path used to locate docker files. Defaults to `.` (root of project)
    # but may be changed a specific directory.
    base_path: str = '.'

    # Name of the docker registry to push the images to. For Github container
    # registry make sure to also include the github owner. For instance:
    # ghcr.io/owner
    docker_registry: str

    # When executing docker build commands we may need to obtain external tokens
    # via other github actions. These can be injected here. We can see those
    # steps in the github workflow file before the actual docker shell scripts
    # are run.
    extra_build_steps: list[dict[str, Any]] | None = None

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

    def update_makefile(self: 'DockerConfig', files: FileNames) -> Res[int]:
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
    ) -> Res[int]:
        """Update the github workflow with the docker images targets.

        Args:
            files: Instance of FileNames to obtain the names of the scripts.

        Returns:
            None if successful, else an issue.
        """
        workflow = Workflow(
            m_dir=files.m_dir,
            ci_dir=files.ci_dir,
            global_env={},
            default_runner=self.default_runner,
            architectures=self.architectures,
            images=self.images,
            extra_build_steps=self.extra_build_steps,
            docker_registry=self.docker_registry,
        )
        # workflow.update_build_job(self.architectures, self.images, files)
        return write_file(files.gh_workflow, str(workflow))

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

    def _write_build_script(
        self: 'DockerConfig',
        file_name: str,
        img: DockerImage,
        m_env: MEnvDocker,
    ) -> Res[None]:
        return one_of(lambda: [
            None
            for script_content in img.ci_build(m_env)
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
        registry = self.docker_registry
        cache_script = create_cache_script(m_env.cache_from_pr, registry)
        push_script = create_push_script(registry)
        script_results = [
            write_file(f'{files.ci_dir}/_find-cache.sh', cache_script),
            write_file(f'{files.ci_dir}/_push-image.sh', push_script),
        ]
        for script_res in script_results:
            if isinstance(script_res, Bad):
                dict_issue = script_res.value.to_dict(show_traceback=False)
                issues.append(dict(dict_issue))
        for img in self.images:
            file_name = f'{files.ci_dir}/{img.image_name}.build.sh'
            write_res = self._write_build_script(file_name, img, m_env)
            if isinstance(write_res, Bad):
                dict_issue = write_res.value.to_dict(show_traceback=False)
                issues.append(dict(dict_issue))
        if issues:
            return issue(
                'write_ci_steps_failure',
                context={'issues': issues},
            )
        return Good(None)

    def write_ci_manifests(
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
        all_manifests: list[str] = []
        for img in self.images:
            manifests = img.ci_manifest(m_env, self.architectures)
            all_manifests.extend(manifests.keys())
            for manifest_key, script in manifests.items():
                file_name = files.ci_manifest(manifest_key)
                write_res = write_file(file_name, script)
                if isinstance(write_res, Bad):
                    dict_issue = write_res.value.to_dict(show_traceback=False)
                    issues.append(dict(dict_issue))
        file_name = f'{files.ci_dir}/manifests.json'
        write_res = write_file(file_name, json.dumps(all_manifests))
        if isinstance(write_res, Bad):
            dict_issue = write_res.value.to_dict(show_traceback=False)
            issues.append(dict(dict_issue))
        if issues:
            return issue(
                'write_ci_manifest_failure',
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
            for _ in self.write_local_steps(files, m_env)
            for _ in self.write_ci_steps(files, m_env)
            for _ in self.write_ci_manifests(files, m_env)
        ])
