import os
try:
    from setuptools import setup, find_packages
except:
    from distutils.core import setup, find_packages

here = os.path.abspath( os.path.dirname( __file__ ) )
README = open(os.path.join( here, 'README.rst' ) ).read()

setup(
    name='chibi_dl',
    version='0.1.3',
    description='',
    long_description=README,
    license='',
    author='dem4ply',
    author_email='',
    packages=find_packages(),
    install_requires=[
        'chibi>=0.11.10', "chibi_requests>=0.1.1",
        'selenium>=3.141.0',
        'undetected-chromedriver>=3.4.6',
    ],
    dependency_links = [],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
    entry_points = {
        'console_scripts': [
            'chibi_dl=chibi_dl.main:main'
        ],
    }
)
