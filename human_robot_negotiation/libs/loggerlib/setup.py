from setuptools import setup, find_packages

setup(name='loggerlib',
      version='0.0.1',
      description='hant_logger_lib',
      author='Berk Buzcu',
      author_email='buzcuberk@gmail.com',
      url='www.example.com',
      install_requires=[
            'peewee',
      ],
      packages=find_packages()
     )