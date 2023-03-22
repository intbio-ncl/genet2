import requests
from app.enhancer.evaluator.abstract_evaluator import AbstractEvaluator

class ReferentialEvaluator(AbstractEvaluator):
    '''
    Finds entities containing dead references (names) or 
    references that do not point to known external entities.
    '''
    def __init__(self, world_graph, miner):
        super().__init__(world_graph, miner)

    def evaluate(self,graph):
        score = self._initial_score
        entities = graph.get_dna()
        increment = self._get_increment(len(entities))
        comments = {}
        for e in entities:
            is_dead = self._is_dead_uri(e.get_key())
            is_reference = self._miner.is_reference(e.get_key())
            if not is_reference and not is_dead :
                comments[e.get_key()] = "Unknown Reference."
            elif is_dead:
                comments[e.get_key()] = "Dead URI."
            else:
                score += increment
        return {"score" : int(score),
                "comments" : comments}


    def _is_dead_uri(self,uri):
        request_response = requests.head(uri)
        return request_response.status_code != 200