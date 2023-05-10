from setuptools import setup
import version

setup(
    name='serial_over_http_client',
    version=version.__version__,
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