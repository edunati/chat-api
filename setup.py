import re

from setuptools import find_packages, setup


REGEXP = re.compile(r"^__version__\W*=\W*'([\d.abrc]+)'")


def read_version():
    with open('VERSION') as fd:
        return fd.read().strip()


install_requires = [
    'aiohttp',
    'aiopg[sa]',
    'aiohttp_graphql',
    'aioredis',
    'aiodataloader',
    'trafaret_config',
    'graphene==2.1.8',
    'graphql-core==2.3.2',
    'graphql-ws',
    'psycopg2-binary',
    'Faker',
]


setup(
    name='graph',
    version=read_version(),
    description='aiohttp chat api',
    packages=find_packages(),
    package_data={
        '': ['config/*.*']
    },
    package_dir={'': '.'},
    py_modules=['graph'],
    entry_points={
        'console_scripts': [
            'aio-api-setup-schemas=graph:main',
            'aio-api-app=graph.start:main',
        ]
    },
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False,
)
