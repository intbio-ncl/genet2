from app.enhancer.data_miner.data_miner import DataMiner
from app.enhancer.canonicaliser.canonicaliser import Canonicaliser
from app.enhancer.evaluator.evaluator import Evaluator
from app.enhancer.enhancements.enhancements import Enhancements

class Enhancer:
    def __init__(self,graph):
        self._graph = graph
        self._miner = DataMiner()
        self._canonicaliser = Canonicaliser(self._graph,self._miner)
        self._evaluator = Evaluator(self._graph,self._miner)
        self._enhancements = Enhancements(self._graph,self._miner)

    def evaluate_design(self,graph_name,flatten=False):
        return self._evaluator.evaluate(graph_name,flatten=flatten)

    def get_evaluators(self):
        evaluators = []
        def ge(evaluator):
            evaluators.append(evaluator)
            for e in evaluator:
                evaluators.append(e)
                ge(e)
        ge(self._evaluator)
        return evaluators

    def canonicalise_graph(self,graph_name,mode="automated"):
        '''
        Attempts to replace nodes or sub-systems with synbiohub records.
        '''
        reps,feedback = self._canonicaliser.design(graph_name,mode=mode)
        return reps,feedback
            
    def canonicalise_entity(self,entity,graph_name,mode="automated"):
        reps,feedback = self._canonicaliser.entity(entity,graph_name,mode=mode)
        return reps,feedback

    def apply_cannonical(self,replacements,graph_name,feedback=None):
        if feedback is not None:
            for k,v in feedback.items():
                if k in replacements.values():
                    self._graph.truth.synonyms.positive(k,v)
                else:
                    self._graph.truth.synonyms.negative(k,v)
        return self._canonicaliser.apply(replacements,graph_name)


    def get_pipeline_names(self):
        return []

    def cast_pipeline(self,names):
        return [self._pipelines[n] for n in names]

    def enhance_design(self,graph_name,mode="automated",pipeline=None):
        return [],{}


    def seed_truth_graph(self):
        '''
        Keep it seperate because it should only need to be loaded once ever.
        '''
        from app.enhancer.seeder import seeder
        seeder.truth_graph(self._graph.truth,self._miner)
    

    def expand_truth_graph(self):
        '''
        Performs an iteration over the truth graph to find enhancements internally.
        '''
        self._enhancements.enhance(self._graph.truth.name)
        #self._canonicaliser.truth_graph()

        pass

