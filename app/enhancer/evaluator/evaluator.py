from app.enhancer.evaluator.abstract_evaluator import AbstractEvaluator
from app.enhancer.evaluator.completeness.completeness import CompletenessEvaluator
from app.enhancer.evaluator.standard.standard import StandardEvaluator


class Evaluator(AbstractEvaluator):
    def __init__(self, world_graph, miner):
        super().__init__(world_graph, miner, evaluators=[CompletenessEvaluator,
                                                         StandardEvaluator])

    def evaluate(self, graph_name,flatten=False):
        dg = self._wg.get_design(graph_name)
        feedback = super().evaluate(dg)
        if not flatten:
            return feedback

        def _flatten(d):
            comments = {}
            if "comments" in d:
                comments = d["comments"]
            if "evaluators" in d:
                for k, v in d["evaluators"].items():
                    if isinstance(v, dict):
                        comments.update(_flatten(v))
            return comments
        for k,v in feedback["evaluators"].items():
            for k1,v1 in v["evaluators"].items():
                feedback["evaluators"][k]["evaluators"][k1]["comments"] = _flatten(v1)        
        return feedback
