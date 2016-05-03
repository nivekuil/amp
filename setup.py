import sys
from distutils.core import setup
from distutils.extension import Extension

if sys.version_info[0] == 2:
    print("Python 2 detected.  The Python 3 version is recommended.")
    base_dir = 'python2'
    pyversion = '2'
elif sys.version_info[0] == 3:
    print("Python 3 detected.")
    base_dir = 'python3'
    pyversion = '3'

setup(
    name='amp-player',
    version='0.1.24-' + pyversion,
    description='Asynchronous command-line YouTube interface',
    keywords=["music", "audio", "video", "stream", "youtube"],
    url='https://github.com/nivekuil/amp',
    download_url='https://github.com/nivekuil/amp/tarball/master',
    author='Kevin Liu',
    author_email='mail@nivekuil.com',
    license='GPL3',
    entry_points={'console_scripts': ['amp = amp.main:main']},
    packages = ['amp'],
    package_dir={
        'amp' : base_dir + '/amp'
    },
    install_requires=['pafy', 'psutil>=4'],
    classifiers = [
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],

)
