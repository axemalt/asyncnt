from setuptools import setup
import re

version = ''
with open('aiont/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')

readme = ''
with open('README.md') as f:
    readme = f.read()

packages = [
    'aiont'
]

setup(name='aiont',
    author='axemalt',
    url='https://github.com/axemalt/aiont',
    version=version,
    packages=packages,
    package_data={'aiont': ['py.typed']},
    license='MIT',
    description='An asynchronous way to fetch team and racer statistics from nitrotype.',
    install_requires=['cloudscraper', 'aiohttp'],
    long_description=readme,
    long_description_content_type="text/x-md",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    python_requires='>=3.7.0',
)