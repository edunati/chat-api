import asyncio

import graphene
from aiohttp_graphql import GraphQLView
from graphql.execution.executors.asyncio import AsyncioExecutor
from graphql_ws.aiohttp import AiohttpSubscriptionServer

from aiohttp import web

from graph.api.queries import Query
from graph.api.mutations import Mutation
from graph.api.subscriptions import Subscription

__all__ = ['GQL', ]


class CustomAiohttpSubscriptionServer(AiohttpSubscriptionServer):

    def get_graphql_params(self, connection_context, *args, **kwargs):
        params = super().get_graphql_params(
            connection_context,
            *args,
            **kwargs,
        )
        params.update({'context_value': connection_context.request_context})

        return params


schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
)

subscription_server = CustomAiohttpSubscriptionServer(schema)


def GQL(graphiql: bool = False) -> GraphQLView:
    '''
    Main view providing access to GraphQl. Modes:

        - Simple GraphQl handler
        - GraphIQL view for interactive work with graph application

    :param graphiql: bool
    :return: GraphQLView
    '''

    gql_view = GraphQLView(schema=schema, executor=AsyncioExecutor(
        loop=asyncio.get_event_loop()), enable_async=True, graphiql=graphiql, socket="ws://localhost:8080/subscriptions",)
    return gql_view


async def subscriptions(request: web.Request) -> web.WebSocketResponse:
    '''
    Handler creates socket connections with apollo client to check
    subscriptions.
    '''
    ws = web.WebSocketResponse(protocols=('graphql-ws',))
    await ws.prepare(request)

    await subscription_server.handle(
        ws,
        request_context={"request": request}
    )

    return ws
