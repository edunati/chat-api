import graphene


__all__ = ['User', ]


class User(graphene.ObjectType):
    '''
    User.
    '''
    id = graphene.Int(
        description='id of user',
    )
    username = graphene.String(
        description='username of user',
    )
    email = graphene.String(
        description='username of user',
    )
    avatar_url = graphene.String(
        description='main user`s photo',
    )
