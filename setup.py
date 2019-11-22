from setuptools import (setup, find_packages)

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='proWES',
    version='0.14.0',
    author='Elixir Europe',
    author_email='alexander.kanitz@alumni.ethz.ch',
    description='GA4GH WES proxy service',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='Apache License 2.0',
    url='https://github.com/elixir-europe/proWES.git',
    packages=find_packages(),
    keywords=(
        'ga4gh wes workflow elixir rest restful api app server openapi '
        'swagger mongodb python flask'
    ),
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=['connexion', 'Flask-Cors', 'Flask-PyMongo'],
)
