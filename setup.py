from setuptools import setup

package_name = 'serial_over_http_client'

setup(
    name=package_name,
    version='0.1',
    description='Sends requests to a HTTP server. The interface partially implements pySerial API.',
    url='https://github.com/dims-poland/serial_over_http',
    author='Michal Vrábel',
    author_email='michal.vrabel@ncbj.gov.pl',
    license='BSD 2-clause',
    packages=[package_name],
    install_requires=[],
    data_files=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.5',
    ],
)