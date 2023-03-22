from app.enhancer.evaluator.abstract_evaluator import AbstractEvaluator

class SequenceEvaluator(AbstractEvaluator):
    '''
    Evaluates how many genetic entities sequence data encoded.
    '''
    def __init__(self, world_graph, miner):
        super().__init__(world_graph, miner)

    def evaluate(self,graph):
        score = self._initial_score
        entities = graph.get_dna()
        increment = self._get_increment(len(entities))
        comments = {}
        for e in entities:
            if not hasattr(e,"hasSequence"):
                comments[e.get_key()] = "No Sequence"
            else:
                score += increment

        return {"score" : int(score),
                "comments" : comments}