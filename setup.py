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
    'aiont',
    'aiont/AioNT'
]

setup(name='aiont',
      author='axemalt',
      url='https://github.com/axemalt/aiont',
      version=version,
      packages=packages,
      license='MIT',
      description='Async Implementation of NT.py',
      install_requires=['cloudscraper', 'jsonpickle'],
      data_files=['aiont/scrapers.json', 'aiont/cars.json'],
      long_description=readme,
      long_description_content_type="text/x-md",
      include_package_data=True,
      python_requires='>=3.8.0',
)