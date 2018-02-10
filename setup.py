import os.path
import re
from setuptools import setup


def get_version(package):
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


setup(
    name="chasgimqtt",
    version=get_version("chasgimqtt"),
    author="Xavier Lesa",
    author_email="xavierlesa@gmail.com",
    url="https://github.com/xavierlesa/channels-asgi-mqtt",
    description="Interface between MQTT broker and ASGI and Channels 2.0 compatible",
    long_description=open("README.md").read(),
    license="GPLv3+",
    packages=["chasgimqtt"],
    install_requires=[
        "paho-mqtt",
    ],
    entry_points={
        "console_scripts": [
            "chasgimqtt=chasgimqtt.cli:main",
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Framework :: Django',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
