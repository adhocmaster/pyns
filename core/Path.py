from core.Client import Client


class Path:

    def __init__(self, id, client=None, nodes=None, server=None):

        self.id = id
        self.client = client
        self._nodes = []
        if nodes is not None:
            self._nodes = nodes
        self.server = server
        self._nodes.append(self.server)

    
    def __str__(self):

        nodeStr = ""
        for node in self._nodes:
            nodeStr += ", " + str(node.id)

        return (
            f" \n\tid: {self.id}"
            f" \n\tclient: {self.client.id}"
            f" \n\tnodes: {nodeStr}"
            f" \n\tserver: {self.server.id}"
        )
    
    def addClient(self, client: Client):
        self.client = Client

    def addNode(self, node):

        self._nodes[-1] = node # pushing server away
        self._nodes.append(self.server)

    
    def getNodesWithServer(self):
        return self._nodes
        
    def getFirstNode(self):
        return self._nodes[0]
    
    def getNextNode(self, nodeId):
        # TODO use a dic to optimize it
        foundNode = False
        for node in self._nodes:
            if foundNode:
                return node # nodeId was the previous one

            if node.id == nodeId:
                foundNode = True

        return None