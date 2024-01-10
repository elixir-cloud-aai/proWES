"""Package setup."""

from pathlib import Path
from setuptools import setup, find_packages

root_dir = Path(__file__).parent.resolve()

with open(root_dir / "pro_wes" / "version.py", encoding="utf-8") as _file:
    exec(_file.read())  # pylint: disable=exec-used

with open(root_dir / "README.md", encoding="utf-8") as _file:
    LONG_DESCRIPTION = _file.read()

with open(root_dir / "requirements.txt", encoding="utf-8") as _file:
    INSTALL_REQUIRES = _file.read().splitlines()

setup(
    name="pro-wes",
    version=__version__,  # type: ignore # noqa: E501 F821 # pylint: disable=undefined-variable
    license="Apache License 2.0",
    description="Proxy/gateway GA4GH WES service",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="ELIXIR Cloud & AAI",
    author_email="cloud-service@elixir-europe.org",
    url="https://github.com/elixir-cloud-aai/proWES.git",
    project_urls={
        "Repository": "https://github.com/elixir-cloud-aai/proWES",
        "ELIXIR Cloud & AAI": "https://elixir-cloud.dcc.sib.swiss/",
        "Tracker": "https://github.com/elixir-cloud-aai/proWES/issues",
    },
    packages=find_packages(),
    keywords=(
        "ga4gh wes proxy rest restful api app server openapi "
        "swagger mongodb python flask"
    ),
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.10",
    ],
    install_requires=INSTALL_REQUIRES,
    setup_requires=["setuptools_git>=1.2"],
)
