import json
import os
from typing import Any

from m.core import Bad, Good, Res, issue, one_of, rw
from m.log import Logger
from pydantic import BaseModel

from .env import MEnvDocker
from .filenames import FileNames
from .gh_workflow_multi import Workflow as MultiWorkflow
from .gh_workflow_single import Workflow as SingleWorkflow
from .image import DockerImage
from .shell_scripts import (
    create_cache_script,
    create_push_script,
    create_push_script_tags,
)
from .tags import docker_tags
from .workflow_input import GithubWorkflowInput

logger = Logger('m.ci.docker.config')


class DockerConfig(BaseModel):
    """Contains information about the docker images to build."""

    # additional environment variables to inject globally.
    global_env: dict[str, str] | None = None

    # default runner to use when creating blueprints and manifests
    default_runner: str = 'ubuntu-22.04'

    # A map of the architectures to build. It maps say `amd64` to a Github
    # runner that will build the image for that architecture.
    #    amd64: Ubuntu 20.04
    architectures: dict[str, str | list[str]] | None

    # A map of the platforms to build. It maps say `amd64` to a valid buildx
    # supported platform. Using this allows us to build multi-arch images using
    # buildx in an environment that may not have the necessary architecture.
    # For instance: 'amd64: linux/amd64'
    platforms: dict[str, str] | None = None

    # Freeform object to allow us to specify a container in which to run
    # the docker commands.
    # https://docs.github.com/en/actions/using-jobs/running-jobs-in-a-container
    # Note that this requires the mounting the following volume
    # - /var/run/docker.sock:/var/run/docker.sock
    # This may be needed for self-hosted runners that may not have python or pip.
    container: dict[str, Any] | None = None

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

    # Additional inputs to the github workflow file.
    workflow_inputs: dict[str, GithubWorkflowInput] | None = None

    # Maximum number of parallel manifests to build.
    # https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs#defining-the-maximum-number-of-concurrent-jobs
    max_parallel_manifests: int | None = None

    # list of images to build
    images: list[DockerImage]

    # https://docs.docker.com/reference/cli/docker/buildx/imagetools/create/
    use_buildx: bool = True

    def makefile_targets(self: 'DockerConfig', files: FileNames) -> str:
        """Create the Makefile targets to trigger the local builds.

        Args:
            files: Instance of FileNames to obtain the names of the scripts.

        Returns:
            A string with the Makefile targets.
        """
        m_dir = files.m_dir
        lines: list[str] = [
            'define m_env',
            f'\t$(eval include {m_dir}/.m/m_env.sh)',
            f'\t$(eval $(cut -d= -f1 {m_dir}/.m/m_env.sh))',
            'endef',
            '',
            'm-env:',
            f'\tmkdir -p {m_dir}/.m && m ci env --bashrc > {m_dir}/.m/m_env.sh',
            '',
            'm-blueprints: m-env',
            '\t$(call m_env)',
            f'\tm blueprints --skip-makefile --skip-workflow {m_dir}',
            f'\tchmod +x {m_dir}/.m/blueprints/local/*.sh\n',
        ]
        for index, img in enumerate(self.images):
            name = img.image_name
            img_file = files.local_file(f'{name}.build.sh')
            previous_img = (
                self.images[index - 1].image_name
                if index > 0
                else None
            )
            dep = f' dev-{previous_img}' if previous_img else ' m-blueprints'
            lines.append(f'dev-{name}:{dep}')
            lines.append('\t$(call m_env)')
            lines.append(f'\t{img_file}\n')
        return '\n'.join(lines)

    def update_makefile(self: 'DockerConfig', files: FileNames) -> Res[int]:
        """Update the Makefile with the docker images targets.

        Args:
            files: Instance of FileNames to obtain the names of the scripts.

        Returns:
            None if successful, else an issue.
        """
        return rw.insert_to_file(
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
        global_env: dict[str, str] = self.global_env or {}
        multi_workflow = MultiWorkflow(
            m_dir=files.m_dir,
            ci_dir=files.ci_dir,
            global_env=global_env,
            default_runner=self.default_runner,
            architectures=self.architectures or {},
            platforms=self.platforms,
            images=self.images,
            extra_build_steps=self.extra_build_steps,
            docker_registry=self.docker_registry,
            extra_inputs=self.workflow_inputs,
            max_parallel_manifests=self.max_parallel_manifests,
            container=self.container,
            use_buildx=self.use_buildx,
        )
        single_workflow = SingleWorkflow(
            m_dir=files.m_dir,
            ci_dir=files.ci_dir,
            global_env=global_env,
            default_runner=self.default_runner,
            images=self.images,
            extra_build_steps=self.extra_build_steps,
            extra_inputs=self.workflow_inputs,
            docker_registry=self.docker_registry,
            container=self.container,
        )
        workflow = multi_workflow if self.architectures else single_workflow
        return rw.write_file(files.gh_workflow, str(workflow))

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
            write_res = _write_local_step(files, img, m_env)
            _append_issue(write_res, issues)
        if issues:
            return issue(
                'write_local_steps_failure',
                context={'issues': issues},
            )
        return Good(None)

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
        push_script = (
            create_push_script(registry)
            if self.architectures
            else create_push_script_tags(registry, m_env.m_tag)
        )
        script_results = [
            rw.write_file(f'{files.ci_dir}/_find-cache.sh', cache_script),
            rw.write_file(f'{files.ci_dir}/_push-image.sh', push_script),
        ]
        for script_res in script_results:
            _append_issue(script_res, issues)
        for img in self.images:
            file_name = f'{files.ci_dir}/{img.image_name}.build.sh'
            write_res = _write_build_script(file_name, img, m_env)
            _append_issue(write_res, issues)
            if self.use_buildx:
                file_name = f'{files.ci_dir}/{img.image_name}.manifest.sh'
                write_res = _write_manifest_script(file_name, img, m_env)
                _append_issue(write_res, issues)
        if issues:
            return issue(
                'write_ci_steps_failure',
                context={'issues': issues},
            )
        return Good(None)

    def write_ci_manifest_info(
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
        if not self.architectures:
            return Good(None)
        m_tag = m_env.m_tag
        if not m_tag and os.environ.get('CI') != 'true':
            logger.warning('M_TAG not found in non-CI environment. Using 1.1.1')
            m_tag = '1.1.1'
        names = [img.image_name for img in self.images]
        tags = [m_tag, *docker_tags(m_tag)]
        names_json = json.dumps(names, separators=(',', ':'))
        tags_json = json.dumps(tags, separators=(',', ':'))
        files_res = [
            rw.write_file(f'{files.ci_dir}/_image-names.json', names_json),
            rw.write_file(f'{files.ci_dir}/_image-tags.json', tags_json),
        ]
        issues: list[dict] = []
        for file_res in files_res:
            _append_issue(file_res, issues)
        if issues:
            return issue(
                'write_ci_manifest_info_failure',
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
            for _ in self.write_ci_manifest_info(files, m_env)
        ])


def _write_build_script(
    file_name: str,
    img: DockerImage,
    m_env: MEnvDocker,
) -> Res[None]:
    return one_of(lambda: [
        None
        for script_content in img.ci_build(m_env)
        for _ in rw.write_file(file_name, script_content)
    ])


def _write_manifest_script(
    file_name: str,
    img: DockerImage,
    m_env: MEnvDocker,
) -> Res[None]:
    return one_of(lambda: [
        None
        for script_content in img.ci_manifest(m_env)
        for _ in rw.write_file(file_name, script_content)
    ])


def _write_local_step(
    files: FileNames,
    img: DockerImage,
    m_env: MEnvDocker,
) -> Res[None]:
    file_name = files.local_file(f'{img.image_name}.build.sh')
    return one_of(lambda: [
        None
        for script_content in img.local_build(m_env)
        for _ in rw.write_file(file_name, script_content)
    ])


def _append_issue(res: Res[Any], issues: list[dict]):
    # helper function to append issue data to a list
    if isinstance(res, Bad):
        dict_issue = res.value.to_dict(show_traceback=False)
        issues.append(dict(dict_issue))
