from distutils.core import setup

setup(
    name='petrify',
    version='0.8.1',
    author='Frank Murphy, et al',
    author_email='fpmurphy@mtu.edu',
    packages=[
        'petrify',
        'petrify.engines',
        'petrify.formats',
        'petrify.plane',
        'petrify.machine',
        'petrify.space'
    ],
    url='http://pypi.python.org/pypi/petrify/',
    license='LICENSE',
    description='a programmatic cad library',
    long_description=open('README.rst').read(),
    install_requires=[
        "pycsg >= 0.3.3",
        "svg.path==3.0",
        "Pint==0.9.0"
    ],
)
