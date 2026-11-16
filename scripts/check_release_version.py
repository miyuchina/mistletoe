"""Verify that a release tag matches the wheel and sdist metadata."""

import argparse
import tarfile
import zipfile
from email.parser import BytesParser
from pathlib import Path


def package_version(path: Path) -> str:
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            names = [name for name in archive.namelist()
                     if name.endswith(".dist-info/METADATA")]
            if len(names) != 1:
                raise SystemExit(f"{path}: expected one wheel metadata file")
            metadata = archive.read(names[0])
    else:
        with tarfile.open(path) as archive:
            names = [name for name in archive.getnames()
                     if name.count("/") == 1 and name.endswith("/PKG-INFO")]
            if len(names) != 1:
                raise SystemExit(f"{path}: expected one top-level PKG-INFO file")
            stream = archive.extractfile(names[0])
            if stream is None:
                raise SystemExit(f"{path}: PKG-INFO is not a file")
            with stream:
                metadata = stream.read()
    version = BytesParser().parsebytes(metadata).get("Version")
    if not version:
        raise SystemExit(f"{path}: missing package version")
    return version


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag", help="Release tag, including its v prefix")
    parser.add_argument("distributions", type=Path, help="Directory containing the distributions")
    args = parser.parse_args()
    if not args.tag.startswith("v"):
        parser.error("release tags must start with v")
    wheels = list(args.distributions.glob("*.whl"))
    sources = list(args.distributions.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sources) != 1:
        raise SystemExit("Expected one wheel and one sdist")
    expected = args.tag.removeprefix("v")
    for path in wheels + sources:
        version = package_version(path)
        if version != expected:
            raise SystemExit(f"{path}: version {version!r} does not match tag version {expected!r}")


if __name__ == "__main__":
    main()
