import re

from setuptools import find_packages, setup


REGEXP = re.compile(r"^__version__\W*=\W*'([\d.abrc]+)'")


def read_version():
    with open('VERSION') as fd:
        return fd.read().strip()


install_requires = [
    'aiohttp==3.6.2',
    'aiopg[sa]==1.0.0',
    'aiohttp_graphql==1.1.0',
    'aioredis==1.3.1',
    'aiodataloader==0.2.0',
    'trafaret_config==2.0.2',
    'graphene==2.1.8',
    'graphql-core==2.3.2',
    'graphql-ws==0.3.1',
    'psycopg2-binary==2.8.5',
    'Faker==4.1.1',
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
