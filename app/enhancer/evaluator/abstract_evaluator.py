class AbstractEvaluator:
    def __init__(self,world_graph,miner,initial_score=0,evaluators=None):
        self._wg = world_graph
        self._miner = miner
        self._initial_score = initial_score
        if evaluators is not None:
            self._evaluators = [e(world_graph,miner) for e in evaluators]
        else:
            self._evaluators = []
        self.name = self.__class__.__name__
    
    def __iter__(self):
        for e in self._evaluators:
            yield e
            
    def evaluate(self,graph):
        scores = []
        feedback = {"evaluators" : {}}
        if len(self._evaluators) == 0:
            return feedback

        for evaluator in self._evaluators:
            feedback["evaluators"][evaluator.name] = evaluator.evaluate(graph)
            scores.append(feedback["evaluators"][evaluator.name]["score"])
        feedback["score"] = int(sum(scores) / len(self._evaluators))
        return feedback
        
    def _get_increment(self,num_checks):
        if num_checks == 0:
            num_checks = 1
        return 100/num_checks