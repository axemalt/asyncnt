from setuptools import setup
import re

version = ''
with open('asyncnt/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')

readme = ''
with open('README.rst') as f:
    readme = f.read()

packages = [
    'asyncnt'
]

setup(name='asyncnt',
    author='axemalt',
    url='https://github.com/axemalt/asyncnt',
    version=version,
    packages=packages,
    package_data={'asyncnt': ['py.typed']},
    license='MIT',
    description='An asynchronous way to fetch data from nitrotype.',
    install_requires=['cloudscraper', 'aiohttp'],
    long_description=readme,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    python_requires='>=3.7.0',
)