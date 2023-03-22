class Procedures():
    def __init__(self, graph):
        self._graph = graph
        self._driver = self._graph.driver

    def dfs(self, name, source, dest=None, mode="stream"):
        return self._driver.procedures.path_finding.dfs(name, source, dest, mode=mode)

    def bfs(self, name, source, dest=None, mode="stream"):
        return self._driver.procedures.path_finding.bfs(name, source, dest, mode=mode)

    def louvain(self,name):
        return self._driver.procedures.community_detection.louvain(name)

    def label_propagation(self,name):
        return self._driver.procedures.community_detection.label_propagation(name)

    def is_connected(self, name):
        return len(set([c["componentId"] for c in 
        self._driver.procedures.community_detection.wcc(name)])) == 1

    def node_similarity(self,name):
        return self._driver.procedures.similarity.node(name)