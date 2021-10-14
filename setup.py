from setuptools import setup
import re

requirements = []
with open('requirements.txt') as f:
  requirements = f.read().splitlines()

version = ''
with open('aiont/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')

readme = ''
with open('README.md') as f:
    readme = f.read()

packages = [
    'discord',
    'discord.types',
    'discord.ui',
    'discord.webhook',
    'discord.ext.commands',
    'discord.ext.tasks',
]

setup(name='aiont',
      author='axemalt',
      url='https://github.com/axemalt/aiont',
      version=version,
      packages=packages,
      license='MIT',
      description='Async Implementation of NT.py',
      long_description=readme,
      long_description_content_type="text/x-md",
      include_package_data=True,
      install_requires=requirements,
      python_requires='>=3.8.0',
)