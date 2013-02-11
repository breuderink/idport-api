from distutils.core import setup

setup(
    name='IDport',
    version='0.1.0',
    author='Boris Reuderink',
    author_email='boris@senzing.com',
    packages=['idport'],
    scripts=[],
    url='https://github.com/breuderink/idport-api',
    license='LICENSE.txt',
    description='Python API for IDport brain-computer interface server',
    long_description=open('README.txt').read(),
    install_requires=[
        'numpy',
        'requests >= 1.1.0',
        'nose',
        'mock'
    ],
)
