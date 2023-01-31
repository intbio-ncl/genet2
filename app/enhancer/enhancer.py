from app.enhancer.data_miner.data_miner import DataMiner
from app.enhancer.evaluator.evaluator import Evaluator
from app.enhancer.enhancements.design_enhancements import DesignEnhancements
from app.enhancer.enhancements.truth_enhancements import TruthEnhancements

class Enhancer:
    def __init__(self,graph):
        self._graph = graph
        self._miner = DataMiner()
        self._evaluator = Evaluator(self._graph,self._miner)
        self._design_enhancements = DesignEnhancements(self._graph,self._miner)
        self._truth_enhancements = TruthEnhancements(self._graph,self._miner)
    
    # --- Evaluate ---
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


    # --- Truth ---
    def seed_truth_graph(self,):
        '''
        Keep it seperate because it should only need to be loaded once ever.
        '''
        from app.enhancer.seeder import seeder
        seeder.truth_graph(self._graph.truth,self._miner)
    
    def enhance_truth(self,mode="automated"):
        self._truth_enhancements.enhance(self._graph.truth.name,mode=mode)

    def apply_truth(self,replacements,graph_name,feedback=None):
        return self._truth_enhancements.apply(replacements,graph_name,feedback=feedback)


    # --- Design ---
    def enhance_design(self,graph_name,mode="automated"):
        return self._design_enhancements.enhance(graph_name,mode=mode)
    
    def apply_design(self,replacements,graph_name,feedback=None):
        return self._design_enhancements.apply(replacements,graph_name,feedback=feedback)

