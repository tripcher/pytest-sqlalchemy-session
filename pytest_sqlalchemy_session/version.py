import os
import sys

# Note that we use ``sys.version_info`` directly,
# because that's how ``mypy`` knows about what we are doing.
if sys.version_info >= (3, 8):  # pragma: py-lt-38
    from importlib import metadata as importlib_metadata
else:  # pragma: py-gte-38
    import importlib_metadata


def get_version(distribution_name: str) -> str:
    """Our helper to get version of a package."""
    return importlib_metadata.version(distribution_name)  # type: ignore


# This is a package name. It is basically the name of the root folder.
pkg_name = os.path.basename(os.path.dirname(__file__))

# We store the version number inside the `pyproject.toml`.
pkg_version = get_version(pkg_name)
