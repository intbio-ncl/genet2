class AbstractEnhancement:
    def __init__(self,world_graph,miner,enhancers=[]):
        self._wg = world_graph
        self._miner = miner
        self._enhancers = [e(self._wg,self._miner) for e in enhancers]
        self.name = self.__class__.__name__
    
    def __iter__(self):
        for e in self._enhancers:
            yield e
            
    def enhance(self,graph):
        enhancements = {}
        if len(self._enhancers) == 0:
            return enhancements
        for evaluator in self._enhancers:
            enhancements[evaluator.name] = evaluator.enhance(graph)
        return enhancements