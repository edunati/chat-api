import asyncio
from aiopg.sa import create_engine, SAConnection
from faker import Faker
import logging
import psycopg2
import random
from typing import List

from graph.utils import get_config
from graph.auth.enums import UserGender

from sqlalchemy.dialects.postgresql import (
    CreateEnumType,
    DropEnumType,
)

from sqlalchemy.schema import (
    CreateTable,
    DropTable,
)

from graph.auth.tables import (
    users,
    gender_enum,
)
from graph.chat.tables import (
    rooms,
    messages,
)


tables = [users, rooms, messages, ]
enums = [gender_enum, ]
faker = Faker()

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
logger = logging.getLogger(__name__)


class AioHttpAppException(BaseException):
    """An exception specific to the AioHttp application."""


class GracefulExitException(AioHttpAppException):
    """Exception raised when an application exit is requested."""


class ResetException(AioHttpAppException):
    """Exception raised when an application reset is requested."""


def handle_sighup() -> None:
    logger.warning("Received SIGHUP")
    raise ResetException("Application reset requested via SIGHUP")


def handle_sigterm() -> None:
    logger.warning("Received SIGTERM")
    raise ResetException("Application exit requested via SIGTERM")


def cancel_tasks() -> None:
    for task in asyncio.Task.all_tasks():
        task.cancel()


async def drop_tables(conn: SAConnection) -> None:

    for table in reversed(tables):
        try:
            await conn.execute(DropTable(table))
        except psycopg2.ProgrammingError:
            pass

    for enum in enums:
        try:
            await conn.execute(DropEnumType(enum))
        except psycopg2.ProgrammingError:
            pass


async def create_tables(conn: SAConnection) -> None:

    for enum in enums:
        await conn.execute(CreateEnumType(enum))

    for table in tables:
        await conn.execute(CreateTable(table))


async def create_local_engine():

    config = get_config()
    config = config['postgres']
    engine = await create_engine(**config)

    return engine


async def generate_users(conn: SAConnection, count: int) -> List[int]:

    values = []
    for number in range(count):
        name = faker.name()
        values.append({
            'username': name,
            'email': f'{name.replace(" ", ".").lower()}@gmail.com',
            'password': 'password',
            'avatar_url': (
                'https://cdn.pixabay.com/photo/2016/08/08/09/17/'
                'avatar-1577909_960_720.png'
            ),
            'gender': random.choice(list(UserGender)).value
        })

    response = await conn.execute(
        users.insert().values(values).returning(users.c.id)
    )

    result = await response.fetchall()

    return [user[0] for user in result]


async def generate_rooms(
        conn: SAConnection,
        count: int,
        users: List[int],
) -> List[int]:

    values = []
    for number in range(count):
        values.append({
            'name': f'room#{number}',
            'owner_id': random.choice(users),
        })

    response = await conn.execute(
        rooms.insert().values(values).returning(rooms.c.id)
    )

    result = await response.fetchall()

    return [room[0] for room in result]


async def generate_messages(
        conn: SAConnection,
        users: List[int],
        rooms: List[int]
) -> None:

    values = []
    for room in rooms:
        for i in range(20):
            values.append({
                'body': faker.text(max_nb_chars=200),
                'who_like': random.sample(users, random.randint(0, 5)),
                'owner_id': random.choice(users),
                'room_id': room,
            })

    await conn.execute(messages.insert().values(values))


async def main_async():
    logger.info("Start to seed data ...")
    engine = await create_local_engine()

    try:
        async with engine.acquire() as conn:
            # create schema
            await drop_tables(conn)
            await create_tables(conn)

            # generate data
            users = await generate_users(conn, 20)
            rooms = await generate_rooms(conn, 20, users)
            await generate_messages(conn, users, rooms)
    finally:
        engine.close()
        await engine.wait_closed()
    logger.info("Finished seeding data!")


def main() -> bool:
    """
    Create Schema and Seed DB
    """
    asyncio.run((main_async()))
