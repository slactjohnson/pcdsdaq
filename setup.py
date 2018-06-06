import versioneer
from setuptools import setup, find_packages

setup(name='pcdsdaq',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      license='BSD',
      author='SLAC National Accelerator Laboratory',
      packages=find_packages(),
      scripts=['bin/pcdsdaq_lib_setup'],
      include_package_data=True,
      description='DAQ Control Interface',
      )
