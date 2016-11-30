from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='mihome',
      version=version,
      description="Xiaomi Mi Home Python bindings",
      long_description="""\
A library to receive paquets, events and to control the Xiaomi Mi Home hub and other devices""",
      classifiers=[
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 3",
          "Intended Audience :: Developers",
          "Intended Audience :: System Administrators",
          "Topic :: System :: Hardware"
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='xiaomi udp paquet iot mi home aqara',
      author='Jonathan Schemoul',
      author_email='jonathan.schemoul@gmail.com',
      url='https://notes.jmsinfor.com/blog/post/admin/Xiaomi-Hub',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "future"
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
