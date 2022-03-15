import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='jmlopez-m',
    version='0.0.0-PLACEHOLDER',
    author='Manuel Lopez',
    author_email='jmlopez.rod@gmail.com',
    description='m',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jmlopez-rod/m',
    project_urls={
        'Bug Tracker': 'https://github.com/jmlopez-rod/m/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_dir={'': 'src'},
    scripts=[
        'bin/m',
        'bin/startRelease',
        'bin/startHotfix',
        'bin/reviewRelease',
        'bin/endRelease',
    ],
    install_requires=['typing_extensions'],
    package_data={'m': ['py.typed']},
    packages=setuptools.find_packages(where='src'),
    python_requires='>=3.8',
)
