from typing import List

import graphene
from graphql import ResolveInfo
from aiopg.sa.result import RowProxy

from graph.api.models.user import User
from graph.chat.db_utils import select_messages_by_room_id


__all__ = ['Message', 'Room', ]


class Message(graphene.ObjectType):
    '''
    Messages.
    '''
    id = graphene.Int(
        description="Unique message id",
    )
    body = graphene.String(
        description="Message text"
    )
    favouriteCount = graphene.Int(
        description="Count of users who favorited the current message",
    )

    owner = graphene.Field(
        User,
        description="Message creator",
    )

    async def resolve_owner(self, info: ResolveInfo) -> List[RowProxy]:
        app = info.context['request'].app

        return await app['loaders'].users.load(self['owner_id'])


class Room(graphene.ObjectType):
    '''
    Chat room.
    '''
    id = graphene.Int(
        description="Unique chat room id.",
    )
    name = graphene.String(
        description="Chat room name.",
    )

    owner = graphene.Field(
        User,
        description='Chat room creator.',
    )
    messages = graphene.List(
        Message,
        description='Chat room messages.',
    )

    async def resolve_owner(self, info: ResolveInfo) -> List[RowProxy]:
        app = info.context['request'].app

        return await app['loaders'].users.load(self['owner_id'])

    async def resolve_messages(self, info: ResolveInfo) -> List[RowProxy]:
        app = info.context['request'].app

        async with app['db'].acquire() as conn:
            return await select_messages_by_room_id(conn, self['id'])
