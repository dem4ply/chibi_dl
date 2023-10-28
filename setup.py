import os
try:
    from setuptools import setup, find_packages
except:
    from distutils.core import setup, find_packages

here = os.path.abspath( os.path.dirname( __file__ ) )
README = open(os.path.join( here, 'README.rst' ) ).read()

setup(
    name='chibi_dl',
    version='0.1.1',
    description='',
    long_description=README,
    license='',
    author='dem4ply',
    author_email='',
    packages=find_packages(),
    install_requires=[
        'chibi>=0.7.7', 'm3u8>=0.3.12', "chibi_requests>=0.1.1",
        'selenium>=3.141.0',
        'ffmpeg-python>=0.2.0', 'pymkv>=1.0.5', 'pycountry>=19.8.18',
        'cfscrape>=1.9.5', 'chibi-marshmallow>=0.0.1',
        'undetected-chromedriver>=3.4.6',
        #'natsort>=7.0.1'
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
