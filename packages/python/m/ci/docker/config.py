from pathlib import Path

from m.core import Bad, Good, Res, issue, one_of
from m.core.rw import insert_to_file, write_file
from pydantic import BaseModel

from .env import MEnvDocker
from .image import DockerImage


class FileNames(BaseModel):
    """Name of files that need to be written."""

    m_dir: str
    local_dir: str
    ci_dir: str
    makefile: str
    gh_workflow: str

    @classmethod
    def create_instance(cls: type['FileNames'], m_dir: str) -> 'FileNames':
        """Create and instance of FileNames.

        Args:
            m_dir: The m directory.

        Returns:
            An instance of FileNames.
        """
        gh_dir = Path(f'{m_dir}/../.github/workflows')
        gh_dir.mkdir(parents=True, exist_ok=True)
        return FileNames(
            m_dir=m_dir,
            local_dir=f'{m_dir}/.m/docker-images/local',
            ci_dir=f'{m_dir}/.m/docker-images/ci',
            makefile=f'{m_dir}/../Makefile',
            gh_workflow=f'{m_dir}/../.github/workflows/m_docker_images.yaml'
        )

    def local_build_step_file(self: 'FileNames', image_name: str) -> str:
        """Generate the name of the file that generates the `image_name`.

        Args:
            image_name: The name of the image to generate.

        Returns:
            The name of the file.
        """
        return f'{self.local_dir}/{image_name}__build.sh'

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

    def _local_make(self: 'DockerConfig', files: FileNames) -> str:
        lines: list[str] = []
        for index, img in enumerate(self.images):
            name = img.image_name
            img_file = files.local_build_step_file(name)
            dep = f' dev-{self.images[index-1].image_name}' if index > 0 else ''
            lines.append(f'dev-{name}:{dep}')
            lines.append(f'\t{img_file}\n')
        return '\n'.join(lines)

    # def _ci_build(self: 'DockerConfig', files: FileNames) -> str:
    #     return f'ci - {files.ci_main}'

    def _write_local_build(
        self: 'DockerConfig',
        file_name: str,
        img: DockerImage,
        m_env: MEnvDocker,
    ) -> Res[None]:
        return one_of(lambda: [
            None
            for script_content in img.local_build(m_env)
            for _ in write_file(file_name, script_content)
        ])

    def _local_steps(
        self: 'DockerConfig',
        files: FileNames,
        m_env: MEnvDocker,
    ) -> Res[None]:
        issues: list[str] = []
        for img in self.images:
            local_script = files.local_build_step_file(img.image_name)
            write_res = self._write_local_build(local_script, img, m_env)
            if isinstance(write_res, Bad):
                issues.append(str(write_res.value))
        if issues:
            return issue(
                'issues writing local files',
                context={'issues': issues},
            )
        return Good(None)

    def _ci_steps(self: 'DockerConfig', files: FileNames) -> Res[None]:
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
        """
        files = FileNames.create_instance(m_dir)
        makefile = files.makefile
        return one_of(lambda: [
            None
            for _ in insert_to_file(
                makefile,
                '\n# START: M-DOCKER-IMAGES\n',
                self._local_make(files),
                '\n# END: M-DOCKER-IMAGES\n',
            )
            # for _ in write_file(files.ci_main, self._ci_build(files))
            for _ in self._local_steps(files, m_env)
            for _ in self._ci_steps(files)
        ])
