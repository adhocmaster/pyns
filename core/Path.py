from core.Client import Client


class Path:

    def __init__(self, id, client=None, nodes=None, server=None):

        self.id = id
        self.client = client
        self.nodes = []
        if nodes is not None:
            self.nodes = nodes
        self.server = server

    
    def addClient(self, client: Client):
        self.client = Client