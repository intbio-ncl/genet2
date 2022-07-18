from app.visualiser.builder.builders.design.interaction_protein import InteractionProteinViewBuilder
from app.visualiser.builder.builders.design.utility import produce_aggregated_interaction_graph
from app.visualiser.builder.builders.design.utility import produce_interaction_graph
from app.graph.utility.model.model import model
from app.graph.utility.graph_objects.node import Node
from app.visualiser.builder.builders.editor.common_builds import build_interaction_uri
from app.visualiser.builder.builders.editor.common_builds import build_properties
from app.visualiser.builder.builders.editor.common_builds import create_consists_of


class EditorInteractionProteinViewBuilder(InteractionProteinViewBuilder):
    def __init__(self, graph):
        super().__init__(graph)

    def build(self):
        pp = model.identifiers.objects.protein
        g = self._subgraph(produce_interaction_graph(self._graph))
        g = produce_aggregated_interaction_graph(g, pp)
        g = self._subgraph(new_graph=g)
        for node in self._graph.get_protein():
            g.add_node(node)
        return g

    def get_edge_types(self):
        return [model.identifiers.objects.repression,
                model.identifiers.objects.activation]

    def get_node_types(self):
        p_p = model.identifiers.objects.protein
        c_id = model.get_class_code(p_p)
        return [p_p] + [k[1]["key"] for k in model.get_derived(c_id)]

    def transform(self, n, v, e):
        et = [str(k) for k in self.get_edge_types()]
        if e not in et:
            return []
        model_code = model.get_class_code(e)
        inputs, outputs = model.interaction_predicates(model_code)
        inputs = [str(i[1]["key"]) for i in inputs]
        outputs = [str(o[1]["key"]) for o in outputs]
        assert(len(inputs) == 1)
        assert(len(outputs) == 1)

        v_node = v[outputs[0]]
        p_gn = "transform_ipwb"
        try:
            self._graph.driver.project.drop(p_gn)
        except ValueError:
            pass
        self._graph.project.interaction(p_gn, direction="REVERSE")
        target_type = str(list(set(et) - set([e]))[0])
        target_p_type, _ = model.interaction_predicates(model.get_class_code(target_type))
        i_preds_i, i_preds_o = model.interaction_predicates(model.get_class_code(e))
        assert(len(target_p_type) == 1)
        assert(len(i_preds_i) == 1)
        assert(len(i_preds_o) == 1)
        target_p_type = str(target_p_type[0][1]["key"])
        i_preds_i = str(i_preds_i[0][1]["key"])
        i_preds_o = str(i_preds_o[0][1]["key"])
        n = n[i_preds_i]
        v = v[i_preds_o]
        n_ints = self._graph.get_interactions(n)
        existing_ints = []
        for ni in n_ints:
            for ie in self._graph.get_interaction_elements(ni.n):
                existing_ints.append((ie.get_type(),ie.v))
        target = Node(target_type, graph_name=self._graph.name)
        paths = min([list(p.values()) for p in self._graph.driver.procedures.path_finding.bfs(p_gn, v_node, target)])
        # Take the closest matches.
        edges = []
        for path in paths:
            atarget = path[-1]
            assert(atarget.get_type() == target_type)
            ins, _ = self._graph.get_interaction_io(atarget)
            for i in ins:
                if i.get_type() == target_p_type:
                    if [i_preds_o,i.v] in existing_ints:
                        continue
                    node_uri = build_interaction_uri(n, i.v, e)
                    i_node = Node(
                        node_uri, e, **build_properties(node_uri, self._graph.name))
                    edges.append((i_node, n, i_preds_i, build_properties(
                        i_preds_i, self._graph.name)))
                    edges.append((i_node, i.v, i_preds_o, build_properties(
                        i_preds_o, self._graph.name)))
                    edges += create_consists_of(i_node, self._graph.name)
        return edges
