#!/usr/bin/python

from distutils.core import setup

setup( name = "pyxdg",
       version = "0.20c1",
       description = "PyXDG contains implementations of freedesktop.org standards in python.",
       maintainer = "Freedesktop.org",
       maintainer_email = "xdg@lists.freedesktop.org",
       url = "http://freedesktop.org/wiki/Software/pyxdg",
       packages = ['xdg'],
       classifiers = [
                "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
                "Programming Language :: Python :: 2.6",
                "Programming Language :: Python :: 2.7",
                "Programming Language :: Python :: 3",
                "Topic :: Desktop Environment",
                ],
     )

