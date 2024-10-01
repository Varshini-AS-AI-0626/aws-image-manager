from .connections import MakeConnections



def make_connection():
    connection_obj = MakeConnections()
    client = connection_obj.client
    return client
