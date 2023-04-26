from setuptools import setup


setup(
    name='serial_over_http_client',
    version='0.1',
    description='Sends requests to a HTTP server. The interface partially implements pySerial API.',
    url='https://github.com/dims-poland/serial_over_http',
    author='Michal Vrábel',
    author_email='michal.vrabel@ncbj.gov.pl',
    license='BSD 2-clause',
    setup_requires=['wheel'],
    install_requires=[],
    data_files=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
    ],
    py_modules=['serial_over_http_client']
)