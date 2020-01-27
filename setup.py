import codecs
import os
import re
import sys

from setuptools import setup  # type: ignore
from setuptools.command.install import install  # type: ignore

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts: str) -> str:
    with codecs.open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


def find_version(*file_paths: str) -> str:
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


VERSION = find_version("phial", "__init__.py")


class VerifyVersionCommand(install):  # type: ignore
    """Custom command to verify that the git tag matches our version."""

    description = "Verify that the git tag matches our version"

    def run(self) -> None:
        tag = os.getenv("GITHUB_REF")

        if tag != VERSION:
            info = "Git tag: {0} != phial version: {1}".format(tag, VERSION)
            sys.exit(info)


setup(
    name="phial-slack",
    version=VERSION,
    url="https://github.com/sedders123/phial/",
    license="MIT",
    author="James Seden Smith",
    author_email="sedders123@gmail.com",
    description="A Slack bot framework",
    long_description=open("README.rst").read(),
    package_data={"phial": ["py.typed"]},
    packages=["phial"],
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    python_requires=">=3.6, != 3.6.1",
    keywords=["Phial", "Slack", "bot", "Slackbot"],
    install_requires=[
        "slackclient>=1.2.1,<2",
        "Werkzeug>=0.14.1,<0.17",
        "typing>=3.6.6",
        "watchdog>=0.9.0,<=0.10",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
    cmdclass={"verify": VerifyVersionCommand},
    project_urls={
        "CI: GitHub Actions": "https://github.com/sedders123/phial/actions",
        "GitHub: Issues": "https://github.com/sedders123/phial/issues",
        "Documentation": "https://phial.dev",
    },
)
