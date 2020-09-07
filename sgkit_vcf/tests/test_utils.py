from pathlib import Path

from sgkit_vcf.utils import temporary_directory


def test_temporary_directory():

    prefix = "prefix-"
    suffix = "-suffix"
    with temporary_directory(suffix=suffix, prefix=prefix) as tmpdir:

        dir = Path(tmpdir)
        assert dir.exists()
        assert dir.name.startswith(prefix)
        assert dir.name.endswith(suffix)

        with open(dir / "file.txt", "w") as file:
            file.write("Hello")

    assert not dir.exists()
