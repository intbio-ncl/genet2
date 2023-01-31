import re
from abc import ABC

class AbstractEnhancement(ABC):
    def __init__(self,world_graph,miner,enhancers=[]):
        self._wg = world_graph
        self._miner = miner
        self._enhancers = [e(self._wg,self._miner) for e in enhancers]
        self.name = self.__class__.__name__
    
    def __iter__(self):
        for e in self._enhancers:
            yield e
            
    def enhance(self,graph_name,mode="automated"):
        res = {}
        if len(self._enhancers) == 0:
            return res
        for evaluator in self._enhancers:
            res[evaluator.name] = evaluator.enhance(graph_name,mode=mode)
        return res
    
    def apply(self,replacements,graph_name):
        for evaluator in self._enhancers:
            evaluator.apply(graph_name,replacements)
    
    def _add_interaction(self,graph,interaction,entities):
        edges = []
        for e,i_type in entities:
            edges.append((interaction,e,i_type))
        graph.add_edges(edges)

    def _add_related_node(self,graph,related,r_type):
        ppn = self._create_uri(related.get_key(),r_type)
        return graph.add_node(ppn,r_type)

    def _create_uri(self,original,i_type):
        it_name = _get_name(i_type).lower()
        return f'{_get_prefix(original)}_{it_name}/1'

    def _potential_change(self,cur_changes,subject,option,score,comment,enabled=False):
        i_dict = {"score" : score,
                  "comment" : comment,
                  "apply" : enabled}
        if subject in cur_changes:
            cur_changes[subject][option] = i_dict
        else:
            cur_changes[subject] = {option : i_dict} 
        return cur_changes

def _get_prefix(subject):
    split_subject = _split(subject)
    if split_subject[-1].isdigit():
        return subject[:-2]
    else:
        return subject

def _get_name(subject):
    split_subject = _split(subject)
    if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
        return split_subject[-2]
    elif len(split_subject[-1]) == 3 and _isfloat(split_subject[-1]):
        return split_subject[-2]
    else:
        return split_subject[-1]


def _split(uri):
    return re.split('#|\/|:', uri)


def _isfloat(x):
    try:
        float(x)
        return True
    except ValueError:
        return False
