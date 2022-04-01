from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()

setup(name='pyKeithleyCtl',
      version='0.1',
      description='Provides an interface to Keithley source meter',
      long_description=readme(),
      author='Henrike Fleischhack',
      author_email='fleischhack@cua.edu',
      packages=['pyKeithleyCtl'],
      install_requires=['pyvisa', 'pyvisa-py', 'pyyaml','numpy', 'pandas'],
      )
