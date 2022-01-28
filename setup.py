import os

from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    long_description = f.read()

setup(
    name='purge-static',
    version='0.2.0',
    packages=find_packages(),

    entry_points={
        'console_scripts': [
            'purge-static = purge_static:main',
        ],
    },

    author='quantum',
    author_email='quantum2048@gmail.com',
    url='https://github.com/quantum5/purge-static',
    description='Find changed static files, show their URLs, and optionally '
                'purge them for you on your CDN.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    keywords='cloudflare cdn static cache purge',
    install_requires=['requests'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
)
