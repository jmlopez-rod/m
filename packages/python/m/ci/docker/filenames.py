from pathlib import Path

from pydantic import BaseModel


class FileNames(BaseModel):
    """Name of files that need to be written."""

    m_dir: str
    local_dir: str
    ci_dir: str
    manifests_dir: str
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
            local_dir=f'{m_dir}/.m/blueprints/local',
            ci_dir=f'{m_dir}/.m/blueprints/ci',
            manifests_dir=f'{m_dir}/.m/blueprints/ci/manifests',
            makefile=f'{m_dir}/../Makefile',
            gh_workflow=f'{m_dir}/../.github/workflows/m.yaml',
        )

    def local_file(self: 'FileNames', filename: str) -> str:
        """Generate the name of a local script.

        Args:
            filename: The name of the file.

        Returns:
            The full name of the file.
        """
        return f'{self.local_dir}/{filename}'
