from setuptools import setup, find_packages
from codecs import open
from os import path
import os
import re
import io

# Get version strip
def read(*names, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

here = path.abspath(path.dirname(__file__))


with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name="panaurus",
    version=find_version("panaurus/__init__.py"),
    author="Gerry Tonkin-Hill, Neil MacAlistair and Chris Ruis",
    author_email="g.tonkinhill@gmail.com",
    description="A pan-genome analysis pipeline",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gtonkinhill/panaurus",
    install_requires=[
              'networkx>=2.0',
              'gffutils',
              'BioPython',
              'joblib',
              'tqdm'
          ],
    python_requires='>=3.6.0',
    packages=['panaurus',
              'squeaky'],
    keywords='pangenome roary bacteria',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    entry_points = {
        'console_scripts': ['panaurus = panaurus.__main__:main',
                            'run_prokka = panaurus.run_prokka:main'],
    },
)
