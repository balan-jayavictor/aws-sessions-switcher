import setuptools
from config import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aws_sessions_switcher",
    version=__version__.get_version(),
    author="Balan Jayavictor",
    author_email="dev.balan.jayavictor@gmail.com",
    description="A tool to help switching between multiple AWS environments easy and seamless",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DEV-BALAN-JAYAVICTOR/aws-sessions-switcher",
    packages=['aws_sessions_switcher', 'config'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    install_requires=[
        'configparser>=5.0.0',
        'boto3>=1.13.24',
        'pyinquirer>=1.0.3,<2',
        'dataclasses>=0.6,<1',
        'argcomplete>=1.11.1,<2',
        'prettytable>=0.7.2,<1'
    ],
    entry_points={
        'console_scripts': [
            'aws-sessions-switcher=aws_sessions_switcher.argument_parser:main',
        ],
    },
)
