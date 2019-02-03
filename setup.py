from distutils.core import setup

setup(
    name='petrify',
    version='0.1.0',
    author='Frank Murphy, et al',
    author_email='fpmurphy@mtu.edu',
    packages=['petrify'],
    url='http://pypi.python.org/pypi/petrify/',
    license='LICENSE',
    description='a programmatic cad library',
    long_description=open('README.rst').read(),
    install_requires=[
        "pycsg >= 0.3.3"
    ],
)
