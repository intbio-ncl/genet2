from dis import dis
from app.dashboards.builder.builders.abstract_view import AbstractViewBuilder
from app.graphs.graph_objects.edge import Edge
from rdflib import RDF

class ViewBuilder(AbstractViewBuilder):
    def __init__(self, builder):
        super().__init__(builder)

    def pruned(self):
        edges = []
        w_predicates = [str(p) for p in self._builder._graph.model.identifiers.predicates]
        blacklist = [str(self._builder._graph.model.identifiers.predicates.consistsOf),str(RDF.type)]
        for edge in self._builder.edges():
            if not bool(set(edge.get_labels()) & set(w_predicates)):
                continue
            if bool(set(edge.get_labels()) & set(blacklist)):
                continue
            edges.append(edge)
        return self._builder.sub_graph(edges)

    def hierarchy(self):
        edges = []
        for edge in self._builder.get_entities():
            children = self._builder.get_children(edge.n)
            if len(children) == 0:
                continue
            for child in children:
                edges.append(child)
        return self._builder.sub_graph(edges)

    def interaction_explicit(self):
        edges = []
        for interaction in self._builder.get_interaction():
            consistsOf = self._builder.get_consistsof(interaction.n)
            if consistsOf == []:
                raise NotImplementedError("Not Implemented.")
            consistsOf = consistsOf[0]
            consistsOf = self._builder.resolve_list(consistsOf.v)
            inputs, outputs = self._builder.get_interaction_io(interaction.n)
            for index, n in enumerate(consistsOf):
                if index == len(consistsOf) - 1:
                    for obj_e in outputs:
                        edges.append(Edge(n.v,obj_e.v,obj_e.get_labels(),**obj_e.get_properties()))
                if index == 0:
                    for obj_e in inputs:
                        edges.append(Edge(obj_e.v,n.v,obj_e.get_labels(),**obj_e.get_properties()))
                    continue
                p_element = consistsOf[index-1].v
                edges.append(Edge(p_element,n.v,obj_e.get_labels(),**obj_e.get_properties()))

        return self._builder.sub_graph(edges)

    def interaction_verbose(self):
        edges = []
        for interaction in self._builder.get_interaction():
            interaction = interaction.n
            inputs, outputs = self._builder.get_interaction_io(interaction)
            for obj in inputs:
                edges.append((Edge(obj.v, interaction, obj.get_labels(), **obj.get_properties())))
            for obj in outputs:
                edges.append((Edge(interaction,obj.v, obj.get_labels(), **obj.get_properties())))
        return self._builder.sub_graph(edges)

    def interaction(self):
        edges = []
        for interaction in self._builder.get_interaction():
            print(interaction)
            int_subj = interaction.n
            int_obj = interaction.v
            inputs, outputs = self._builder.get_interaction_io(int_subj)
            if len(outputs) == 0:
                continue
            for inp in inputs:
                for out in outputs:
                    edges.append(Edge(inp.v, out.v, int_obj.get_labels(),**int_obj.get_properties()))
            print("\n\n")
        return self._builder.sub_graph(edges)

    def interaction_genetic(self):
        genetic_pred = self._builder._graph.model.identifiers.objects.DNA
        return self._produce_interaction_graph(genetic_pred)

    def interaction_protein(self):
        p_pred = self._builder._graph.model.identifiers.objects.protein
        return self._produce_interaction_graph(p_pred, True)

    def interaction_io(self):
        edges = []
        i_graph = self.interaction()
        genetic_pred = self._builder._graph.model.identifiers.objects.DNA
        d_pred = self._builder._graph.model.identifiers.predicates.direction
        inputs = []
        for n in i_graph.nodes():
            if len([*i_graph.in_edges(n)]) > 0:
                continue
            i_type = self._builder.get_rdf_type(n)[0].v.get_labels()
            if i_type == genetic_pred or self._builder._graph.model.is_derived(i_type,genetic_pred):
                continue
            inputs.append(n)
        for inp in inputs:
            dfs = list(i_graph.bfs(inp))
            for (n, v) in dfs:
                i_type = self._builder.get_rdf_type(v)[0].v.get_labels()
                if i_type == genetic_pred or self._builder._graph.model.is_derived(i_type,genetic_pred):
                    continue
                if [d[0] for d in dfs].count(v) == 0:
                    edges.append(Edge(inp,v,d_pred))
        return self._builder.sub_graph(edges)


    def _produce_interaction_graph(self, predicate, first_pred=False):
        edges = []
        i_graph = self.interaction()
        g_code = [self._builder._graph.model.get_class_code(predicate)]
        for node in i_graph.nodes():
            n_type = self._builder.get_rdf_type(node)
            if len(n_type) == 0:
                continue
            n_type = n_type[0]
            if not self._builder._graph.model.is_derived(n_type.v.get_labels(), g_code):
                continue
            for e in self._find_nearest_interaction(node, g_code, i_graph, first_pred):
                edges.append(Edge(node,e.v,e.get_labels(),**e.get_properties()))
        g = self._builder.sub_graph(edges)
        g.remove_isolated_nodes()
        return g

    def _find_nearest_interaction(self, node, target_types, graph, use_first=False):
        def _find_nearest_inner(c_node, index=0, first_pred=None):
            i_targets = []
            for edge in graph.edges(c_node):
                # Self Loops.
                if edge.n == edge.v:
                    continue
                if index == 0:
                    first_pred = edge.get_labels()
                node_type = self._builder.get_rdf_type(edge.v)
                if node_type == []:
                    continue
                node_type = node_type[0].v.get_labels()
                if self._builder._graph.model.is_derived(node_type, target_types):
                    if use_first:
                        e = first_pred
                    i_targets.append((edge,index))
                    continue
                i_targets += _find_nearest_inner(edge.v, index+1, first_pred)
            return i_targets

        targets = _find_nearest_inner(node)
        f_targets = []
        # Remove paths to same object (Remove longest.)
        if len(targets) < 2:
            return [t[0] for t in targets]
        for index1, (edge,distance1) in enumerate(targets):
            if [t[0].v for t in targets].count(edge.v) == 1:
                f_targets.append(edge)
                continue
            for index2, (edge2,distance2) in enumerate(targets):
                if index1 == index2:
                    continue
                if edge.v != edge2.v:
                    continue
                if distance2 > distance1:
                    f_targets.append(edge)
                elif distance1 > distance2:
                    f_targets.append(edge2)
                else:
                    f_targets.append(edge)
                    f_targets.append(edge2)
        return f_targets
