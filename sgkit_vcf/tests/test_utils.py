import os
import tempfile
from pathlib import Path

import pytest

from sgkit_vcf.utils import temporary_directory


def directory_with_file_scheme() -> str:
    return f"file:/{tempfile.gettempdir()}"


def directory_with_missing_parent() -> str:
    # create a local temporary directory using Python tempfile
    with tempfile.TemporaryDirectory() as dir:
        pass
    # we know it doesn't exist
    assert not Path(dir).exists()
    return dir


@pytest.mark.parametrize(
    "dir", [None, directory_with_file_scheme(), directory_with_missing_parent()],
)
def test_temporary_directory(dir):
    prefix = "prefix-"
    suffix = "-suffix"
    with temporary_directory(suffix=suffix, prefix=prefix, dir=dir) as tmpdir:
        dir = Path(tmpdir)
        assert dir.exists()
        assert dir.name.startswith(prefix)
        assert dir.name.endswith(suffix)

        with open(dir / "file.txt", "w") as file:
            file.write("Hello")

    assert not dir.exists()


def test_temporary_directory__no_permission():
    # create a local temporary directory using Python tempfile
    with tempfile.TemporaryDirectory() as dir:
        os.chmod(dir, 0o444)  # make it read-only
        with pytest.raises(PermissionError):
            with temporary_directory(dir=dir):
                pass  # pragma: no cover
