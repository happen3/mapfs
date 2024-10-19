from setuptools import setup, Extension

module = Extension('pyfileattr', sources=['pyfileattr.c'])

setup(
    name='pyfileattr',
    version='1.0',
    description='Python interface to file attribute functions in C',
    ext_modules=[module],
)
