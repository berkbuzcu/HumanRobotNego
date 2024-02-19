from distutils.core import setup

setup(name='hant_queue_lib',
      version='0.0.1',
      description='hant_queue_lib',
      author='Berk Buzcu',
      author_email='buzcuberk@gmail.com',
      url='www.example.com',
      install_requires=[
            'pika',
      ],
      py_modules=["queuelib.queue_manager", "queuelib.message", "queuelib.enums"],
     )