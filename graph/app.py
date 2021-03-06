from functools import partial

import aiopg.sa
from aiohttp import web
import aioredis


from graph.routes import init_routes
from graph.utils import init_config
from graph.api.dataloaders import UserDataLoader


async def init_database(app: web.Application) -> None:
    '''
    Creates connection with database.
    '''
    config = app['config']['postgres']

    engine = await aiopg.sa.create_engine(**config)
    app['db'] = engine


async def init_redis(app: web.Application) -> None:
    '''
    Creates connection with redis.
    '''
    config = app['config']['redis']

    sub = await aioredis.create_redis(
        f'redis://{config["host"]}:{config["port"]}'
    )
    pub = await aioredis.create_redis(
        f'redis://{config["host"]}:{config["port"]}'
    )

    create_redis = partial(
        aioredis.create_redis,
        f'redis://{config["host"]}:{config["port"]}'
    )

    app['redis_sub'] = sub
    app['redis_pub'] = pub
    app['create_redis'] = create_redis


async def close_database(app: web.Application) -> None:
    '''
    Closes connection with database before shutdown.
    '''
    app['db'].close()
    await app['db'].wait_closed()


async def close_redis(app: web.Application) -> None:
    '''
    Closes connection with redis before shutdown.
    '''
    app['redis_sub'].close()
    app['redis_pub'].close()


async def init_graph_loaders(app: web.Application) -> None:
    '''
    Initialize data loaders for `graphene`. Initialized
    after db is initialized. 
    '''
    engine = app['db']

    class Loaders:
        users = UserDataLoader(engine, max_batch_size=100)

    app['loaders'] = Loaders()


def init_app() -> web.Application:
    app = web.Application()

    init_config(app)
    init_routes(app)

    app.on_startup.extend([init_redis, init_database, init_graph_loaders])
    app.on_cleanup.extend([close_redis, close_database])

    return app
