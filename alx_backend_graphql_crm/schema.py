



# Minimal schema for Task 0 compliance
import graphene

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")

schema = graphene.Schema(query=Query)
