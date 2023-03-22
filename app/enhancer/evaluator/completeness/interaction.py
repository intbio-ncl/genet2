import re
import uuid
from neo4j.exceptions import ClientError
from app.enhancer.evaluator.abstract_evaluator import AbstractEvaluator
from app.graph.utility.model.model import model
ids = model.identifiers

part_int_map = {
    str(ids.objects.promoter): [str(ids.objects.activation)],
    str(ids.objects.cds): [str(ids.objects.genetic_production)],
    str(ids.objects.protein): [str(ids.objects.repression)],
    str(ids.objects.complex): [str(ids.objects.activation)],
    str(ids.objects.smallmolecule): [str(ids.objects.binds)]
}

nv_i = model.identifiers.objects.input
nv_o = model.identifiers.objects.output
class InteractionEvaluator(AbstractEvaluator):
    '''
    Evalualtes the presence and completeness of functional 
    information namely interactions between physcial entities.
    '''

    def __init__(self, world_graph, miner):
        super().__init__(world_graph, miner, evaluators=[
            PathwayEvaluator, ExpectedInteractionEvaluator])


class PathwayEvaluator(AbstractEvaluator):
    def __init__(self, world_graph, miner):
        super().__init__(world_graph, miner)

    def evaluate(self, graph):
        score = self._initial_score
        comments = {}
        inputs = []
        outputs = []

        proj_name = str(uuid.uuid4())
        try:
            graph.project.interaction(proj_name)
        except ClientError:
            comments['Design'] = ("No Interactions encoded.")
            return {"score": 0,"comments": comments}

        if not graph.procedure.is_connected(proj_name):
            comments['Design'] = ("Design pathway is unconnected."
                                  "Likely because multiple designs encoded or missing interactions.")
            return {"score": 0,
                    "comments": comments}

        for pe in graph.get_physicalentity():
            ints = graph.get_interactions(pe)
            if len(ints) == 0:
                continue

            dirs = []
            for interaction in ints:
                i, o = graph.get_interaction_io(interaction.n)
                # Directionless interaction or self loop (eg protein degradation)
                if len(i + o) == 1:
                    continue
                dirs.append(graph.get_interaction_directions(interaction)[1]["key"])
            dirs = list(set(dirs))
            if len(dirs) != 1:
                continue
            direction = dirs[0]
            if direction == nv_i:
                inputs.append(pe)
            elif direction == nv_o:
                outputs.append(pe)
            else:
                raise ValueError(f'{direction} is unknown.')

        if len(inputs) + len(outputs) == 0:
            score = 50
            comments["Design"] = f'Cycle Pathway, Can not derive pathways because no Inputs or Outputs.'
            return {"score": int(score),
                    "comments": comments}
        if len(inputs) == 0:
            comments["Design"] = f'Cyclic Pathway, No Inputs explicity defined.'
            for o in outputs:
                inputs += self._interaction_walk_i(o, graph)

        elif len(outputs) == 0:
            # Set outputs as nodes that connect to the node the input connects to
            # (See notebook) its essentially the node which edge makes it a cycle.
            comments["Design"] = f'Cyclic Pathway, No Inputs explicity defined.'
            for i in inputs:
                outputs += self._interaction_walk_o(i, graph)                
        increment = self._get_increment(len(inputs))
        for input in inputs:
            paths = graph.procedure.dfs(proj_name, input, outputs)
            p_eles = [item for path in paths for item in path["path"]]
            if len(set(outputs) & set(p_eles)) == 0:
                comments[input.get_key()] = f'No outputs ({",".join([str(s) for s in outputs])}) are affected by this input.'
            else:
                score += increment

        return {"score": int(score),
                "comments": comments}

    def _interaction_walk_i(self, pe, graph):
        seens = []
        f_inps = []
        def _walk(spe):
            nonlocal f_inps
            ints = graph.get_interactions(spe)
            ins = [i for i in ints if graph.get_interaction_directions(i)[1]["key"] == nv_i]
            outs = [i for i in ints if graph.get_interaction_directions(i)[1]["key"] == nv_o]
            for o in outs:
                inps,_ = graph.get_interaction_io(o.n)
                for inp in inps:
                    if inp.v in seens:
                        f_inps += [i.v for i in ins if i.v not in seens]
                        return
                    seens.append(o.v)
                    _walk(inp.v)
        _walk(pe)
        return f_inps

    def _interaction_walk_o(self, pe, graph):
        seens = []
        f_inps = []
        def _walk(spe):
            nonlocal f_inps
            ints = graph.get_interactions(spe)
            ins = [i for i in ints if graph.get_interaction_directions(i)[1]["key"] == nv_i]
            outs = [i for i in ints if graph.get_interaction_directions(i)[1]["key"] == nv_o]
            for i in ins:
                _,outs = graph.get_interaction_io(i.n)
                for out in outs:
                    if out.v in seens:
                        f_inps += [i.v for i in ins if i.v not in seens]
                        return
                    seens.append(i.v)
                    _walk(out.v)
        _walk(pe)
        return f_inps
            


# Decided not to provide suggestions here, this is just evaluation not enhancement.
# For example, this promoter likely activates these downstream CDS etc.
# The interaction suggestions are stretching already.
class ExpectedInteractionEvaluator(AbstractEvaluator):
    def __init__(self, world_graph, miner):
        super().__init__(world_graph, miner)

    def evaluate(self, graph):
        score = self._initial_score
        comments = {}
        entities = graph.get_by_type(list(part_int_map.keys()))
        increment = self._get_increment(len(entities))
        for e in entities:
            ints = [e.n.get_type() for e in graph.get_interactions(e)]
            if len(ints) == 0:
                comments[e.get_key()] = ('No interactions, likely: '
                                     f'{", ".join([_get_name(i) for i in part_int_map[e.get_type()]])}')
                continue
            else:
                score += increment

            isect = list(set(part_int_map[e.get_type()]) - set(ints))
            if len(isect) > 0:
                comments[e.get_key()] = (f'Potentially missing '
                                         f'interactions: {", ".join([_get_name(i) for i in isect])}')
                continue
        return {"score": int(score),
                "comments": comments}


def _get_name(subject):
    split_subject = _split(subject)
    if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
        return split_subject[-2]
    else:
        return split_subject[-1]


def _split(uri):
    return re.split('#|\/|:', uri)
