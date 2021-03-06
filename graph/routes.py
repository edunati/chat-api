from graph.api.views import (
    GQL,
    subscriptions,
)


def init_routes(app):
    add_route = app.router.add_route

    add_route('*', '/graphql', GQL(), name='graphql')
    add_route('*', '/graphiql', GQL(graphiql=True), name='graphiql')
    add_route('*', '/subscriptions', subscriptions, name='subscriptions')
