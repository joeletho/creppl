# setup.py

from setuptools import setup, find_packages

setup(name="creppl",
      version="1.0.0",
      description="C++ REPL",
      long_description="C++ REPL (Read, Evaluate, Print, Loop) written in Python",
      readme="README.md",
      authors="Joel Thomas",
      author_email="joelthomas.e@gmail.com",
      packages=find_packages(),
      keywords=["c++", "repl", "python", "cpp", "cli", "terminal"],
      classifiers=[
          "Topic :: Text Editors",
          "Environment :: Console",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python :: 3.8",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
      ]
      )
