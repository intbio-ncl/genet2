import re
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
    
    def _add_interaction(self,graph,interaction,entities,modifier):
        edges = []
        for e,i_type in entities:
            edges.append((interaction,e,i_type))
        graph.add_edges(edges,modifier)

    def _add_related_node(self,graph,related,r_type):
        ppn = self._create_uri(related.get_key(),r_type)
        return graph.add_node(ppn,r_type)

    def _create_uri(self,original,i_type):
        it_name = _get_name(i_type).lower()
        return f'{_get_prefix(original)}_{it_name}/1'


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
