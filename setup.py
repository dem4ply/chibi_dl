import os
try:
    from setuptools import setup, find_packages
except:
    from distutils.core import setup, find_packages

here = os.path.abspath( os.path.dirname( __file__ ) )
README = open(os.path.join( here, 'README.rst' ) ).read()

setup(
    name='chibi_dl',
    version='0.0.3',
    description='',
    long_description=README,
    license='',
    author='dem4ply',
    author_email='',
    packages=find_packages(),
    install_requires=[
        'chibi>=0.5.4', 'm3u8>=0.3.12',
        'selenium>=3.141.0', 'beautifulsoup4>=4.8.0',
        'ffmpeg-python>=0.2.0', 'pymkv>=1.0.5', 'pycountry>=19.8.18',
        'cfscrape>=1.9.5'
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
