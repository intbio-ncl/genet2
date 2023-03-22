from app.graph.utility.model.model import model
from app.enhancer.evaluator.abstract_evaluator import AbstractEvaluator

class TypeEvaluator(AbstractEvaluator):
    '''
    Finds parts that don't encode genetic roles (promoter, RBS etc.).
    '''
    def __init__(self, world_graph, miner):
        super().__init__(world_graph, miner)

    def evaluate(self,graph):
        score = self._initial_score
        entities = [e for e in graph.get_dna() if graph.get_children(e) == []]
        increment = self._get_increment(len(entities))
        comments = {}
        for e in entities:
            if e.get_type() == str(model.identifiers.objects.dna):
                comments[e.get_key()] = "Ambigous DNA type."
            else:
                score += increment

        return {"score" : int(score),
                "comments" : comments}


