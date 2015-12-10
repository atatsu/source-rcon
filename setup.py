from setuptools import setup


setup(
    name='source-rcon',
    version='0.0.0',
    url='https://github.com/atatsu/source-rcon',
    license='MIT',
    author='Nathan Lundquist',
    author_email='nathan.lundquist@gmail.com',
    description="Python client implementation of Valve's Source RCON Protocol",
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Topic :: Communications',
        'Topic :: Internet',
        'Topic :: Software Development :: Libaries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
    ],
    packages=['srcrcon'],
    keywords='rcon',
    install_requires=[
        'tornado',
        'colorama',
    ]
)
