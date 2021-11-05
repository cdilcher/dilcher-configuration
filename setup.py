import setuptools

with open("Readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
  name="dilcher-configuration",       # Replace with your own username
  version="0.6.4",
  author="Philipp Freyer",
  author_email="philipp.freyer@dilcher.de",
  description="The dilcher-configuration Django app is used to provide easily manageable settings for Django projects.",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/cdilcher/dilcher-configuration",
  packages=setuptools.find_packages(),
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
  ],
  python_requires='>=3.6',
  install_requires=[
    "Django>=3.0.0"
  ],
)
