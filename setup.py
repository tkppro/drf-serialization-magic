import os
import re
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

__name__ = "drf-serialization-magic"
__description__ = (
    "Open package for Django Rest Framework to reduce the duplication of code when working with Serializer"
)
__url__ = "https://github.com/tkppro/drf-serialization-magic"
__author__ = "Thang Dang Minh"
__author_email__ = "thangdangdev@gmail.com"
__license__ = "BSD"


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    package_dir = os.path.join(here, package)
    init_py = open(os.path.join(package_dir, "__init__.py")).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(
        1
    )


def get_package():
    return find_packages(exclude=["tests*"])


def read_file(f):
    with open(f, "r", encoding="utf-8") as fh:
        long_description = fh.read()
        return long_description


package = get_package()
version = get_version(package[0])

if sys.argv[-1] == "publish":
    if os.system("pip freeze | grep wheel"):
        print("wheel not installed.\nUse `pip install wheel`.\nExiting.")
        sys.exit()
    if os.system("pip freeze | grep twine"):
        print("twine not installed.\nUse `pip install twine`.\nExiting.")
        sys.exit()
    os.system("python -m build")
    os.system("twine check dist/*")
    os.system("twine upload dist/*")
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()


setup(
    name=__name__,
    version=version,
    packages=package,
    description=__description__,
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    author=__author__,
    author_email=__author_email__,
    url=__url__,
    license=__license__,
    python_requires=">=3.7",
    install_requires=[
        "Django>=3.0",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet :: WWW/HTTP",
    ],
)
