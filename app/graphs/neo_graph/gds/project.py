import random
import re
from string import ascii_lowercase

presets = ["hierarchy",
"interaction",
"interaction_ppi",
"interaction_genetic"
]

class ProjectBuilder():
    def __init__(self, graph):
        self._graph = graph
        self._ids = self._graph.ids
        self._model = self._graph.model
        self._driver = self._graph.driver
        self._qry_builder = self._graph.qry_builder
        self._procedures = self._graph.procedure

    def get_projected_names(self):
        res = self._driver.graph.list()
        return (list(res["graphName"]))

    def get_presets(self):
        return presets
        
    def get_graph(self, graph_name):
        return self._driver.graph.get(graph_name)

    def project(self, name, nodes, edges, **kwargs):
        return self._driver.graph.project(name, nodes, edges, **kwargs)

    def cypher_project(self, name, n, e):
        qry = self._qry_builder.cypher_project(name, n, e)
        ret = self._run(qry)
        return self.get_graph(name)

    def preset(self,name,preset,**kwargs):
        func = getattr(self, preset)
        return func(name,**kwargs)
        
    def sub_graph(self, o_name, n_name, nodes, edges):
        qry = self._qry_builder.subgraph(o_name, n_name, nodes, edges)
        ret = self._run(qry)
        return self.get_graph(n_name)

    def drop(self, name):
        g = self.get_graph(name)
        g.drop()
        
    def mutate(self, name, types, mutate_type, node_labels=None):
        if node_labels and not isinstance(node_labels, list):
            node_labels = [str(node_labels)]
        qry = self._qry_builder.mutate(name, types, mutate_type, node_labels)
        return self._run(qry)

    def hierarchy(self,name,direction="NATURAL"):
        e = {self._ids.predicates.has_part:{"orientation" : direction}}
        n = []
        for edge in self._graph.edge_query(e=self._ids.predicates.has_part):
            n += [str(edge.n),str(edge.v)]
        n = list(set(n))
        return self._project(name,n,e)[0]

    def interaction(self,name,direction="DIRECTED",type="bipartite"):
        i_name = ''.join(random.choice(ascii_lowercase) for i in range(10))
        graph,ints,pet = self._interaction_direction(i_name,direction.upper())
        nodes = []
        edges = []
        if type.lower() == "bipartite":
            for int,(i,o) in ints.items():
                for inp in i:
                    nodes.append(inp.n.get_key())
                    nodes.append(inp.v.get_key())
                    edges.append(inp.get_type())
                for out in o:
                    nodes.append(out.n.get_key())
                    nodes.append(out.v.get_key())
                    edges.append(out.get_type())
            graph = self.sub_graph(i_name,name,nodes,edges)
        elif type.lower() == "monopartite":
            seens = []
            for interaction,(i,o) in ints.items():
                it = interaction.get_type()
                if it in seens:
                    continue
                seens.append(it)
                types = self._reduce([e.get_type() for e in i+o])
                self.mutate(i_name,types,it)
            # Project Aggregation.
            graph = self.sub_graph(i_name,name,pet,seens)
        self.drop(i_name)
        return graph

    def interaction_ppi(self,name,direction="DIRECTED",type="bipartite"):
        i_name = ''.join(random.choice(ascii_lowercase) for i in range(10))
        graph,ints,pet = self._interaction_direction(i_name,direction.upper())
        p_obj = [str(self._ids.objects.protein)]
        if type.lower() == "bipartite":
            graph = self._interaction_bipartite(graph,i_name,name,ints,p_obj)
        elif type.lower() == "monopartite":
            graph = self._interaction_monopartite(graph,i_name,name,ints,p_obj)
        self.drop(i_name)
        return graph

    def interaction_genetic(self,name,direction,type):
        i_name = ''.join(random.choice(ascii_lowercase) for i in range(10))
        graph,ints,pet = self._interaction_direction(i_name,direction.upper())
        dna_obj = self._ids.objects.dna
        g_objs = [str(dna_obj)] + [str(k[1]["key"]) for k in self._model.get_derived(dna_obj)]
        if type.lower() == "bipartite":
            graph = self._interaction_bipartite(graph,i_name,name,ints,g_objs)
        elif type.lower() == "monopartite":
            graph = self._interaction_monopartite(graph,i_name,name,ints,g_objs)
        self.drop(i_name)
        return graph
    
    def _interaction_direction(self,name,direction):
        nodes = []
        pet = []
        e = {}
        if direction == "NATURAL":
            di = "NATURAL"
            do = "NATURAL"
        elif direction == "DIRECTED":
            di = "REVERSE"
            do = "NATURAL"
        elif direction == "UNDIRECTED":
            di = "UNDIRECTED"
            do = "UNDIRECTED"
        interactions = {i:self._get_interaction_io(i) for i in self._graph.get_interactions()}
        for interaction,io in interactions.items():
            inps,outs = io
            nodes.append(interaction.get_key())
            for i in inps:
                nodes.append(i.v.get_key())
                nodes.append(i.v.get_type())
                pet.append(i.v.get_type())
                i = str(i.get_type())
                if i not in e:
                    e[i] = {"orientation" : di}
            for o in outs:
                nodes.append(o.v.get_key())
                nodes.append(o.v.get_type())
                pet.append(o.v.get_type())
                o = str(o.get_type())
                if o not in e:
                    e[o] = {"orientation" : do} 
        return self._project(name,nodes,e)[0],interactions,list(set(pet))

    def _interaction_bipartite(self,graph,o_name,n_name,interactions,objs):
        int_map,objs = self._interaction(graph,interactions,objs)
        f_interactions = []
        for interaction,paths in int_map.items():
            for path in paths:
                node_label = path[0]
                if len(path) <= 1:
                    continue
                i_node,epath,dest = self._derive_edgelists(interaction,path)
                el1 = epath[0:path.index(i_node)]
                el2 = epath[path.index(i_node):]
                i_type = self._unique_interaction_type(el1[-1],node_label,dest)
                o_type = self._unique_interaction_type(el2[0],node_label,dest)
                f_interactions.append(i_type)
                f_interactions.append(o_type)
                objs.append(i_node.get_key())
                self.mutate(o_name,el1,i_type,node_labels=node_label)
                self.mutate(o_name,el2,o_type,node_labels=i_node.get_key())
        graph = self.sub_graph(o_name,n_name,objs,f_interactions)
        return graph
    
    def _interaction_monopartite(self,graph,o_name,n_name,interactions,objs):
        '''
        Note: Potential issue point.
        https://community.neo4j.com/t/collapsepath-multiple-paths-to-one-type/56270
        This means the relationship names must be unique.
        '''
        f_interactions = []
        int_map,objs = self._interaction(graph,interactions,objs)
        for interaction,paths in int_map.items():
            for path in paths:
                node_label = path[0]
                # No outgoings.
                if len(path) <= 1:
                    continue
                i_type,path,dest = self._derive_edgelist(interaction,path)
                i_type = self._unique_interaction_type(i_type,node_label,dest)
                f_interactions.append(i_type)
                r = self.mutate(o_name,path,i_type,node_labels=node_label)
        # Project Aggregation.
        graph = self.sub_graph(o_name,n_name,objs,f_interactions)
        return graph
    
    def _interaction(self,graph,interactions,objs):
        int_map = {}
        objs = list(set([i.v.get_type() for int,(inps,outs) in interactions.items() for i in inps if i.v.get_type() in objs]))
        #o_instances = self._graph.node_query(objs)
        for interaction,(inps,outs) in interactions.items():
            if len(set([i.v.get_type() for i in inps]) & set(objs)) == 0:
                continue
            for i in inps:
                if i.v.get_type() not in objs:
                    continue
                paths = self._procedures.path_finding.dijkstra_sp(graph,i.n,objs)
                if len(paths) == 0:
                    continue
                paths = sorted([n["path"] for n in paths], key=len)
                f_paths = [paths[0]]
                end_nodes = [paths[0][-1]]
                for path in paths[1:]:
                    if len(list(set(end_nodes) & set(path))) == 0:
                        f_paths.append(path)
                        end_nodes.append(path[-1])
                int_map[interaction] = [[i.v] + p for p in f_paths]
        return int_map,objs

    def _unique_interaction_type(self,i_type,source,dest):
        return i_type + f"/{_get_name(source)}/{_get_name(dest)}"

    def _derive_edgelist(self,interaction,path):
        '''
        Projections dont encode relationship labels but nodelists.
        Derives an edgelist from nodelist using persistent graph.
        Also calculates aggregated interaction type via walk.
        1. Start with input interaction type.
        2. If a repression interaction is found flip the return interaction type.
        Can return repression, activation or input interaction         if direction.upper() == "DIRECTED":
            direction = 
        '''
        def _flip():
            if repression_obj == node.get_type():
                if i_type == repression_obj:
                    return activation_obj
                return repression_obj
            if activation_obj == node.get_type():
                if i_type == orig_type and i_type != repression_obj:
                    return activation_obj
            return i_type

        repression_obj = str(self._ids.objects.repression)
        activation_obj = str(self._ids.objects.activation)
        i_type = interaction.get_type()
        orig_type = i_type
        edgelist = []
        for index,node in enumerate(path):
            if index >= 2:
                i_type = _flip()
            if index >= len(path) - 1:
                return i_type,edgelist,node
            v_node = path[index+1]
            ret_val = self._graph.edge_query(n=node,v=v_node,
                                directed=False,exclusive=True)
            edgelist.append(ret_val[0].get_type())
        raise ValueError(f'Inputed path is empty.')

    def _derive_edgelists(self,interaction,path):
        '''
        Same as derive_edgelist but returns two edgeslist inbetween a node 
        (Interaction node for bipartite graphs)
        '''
        repression_obj = str(self._ids.objects.repression)
        activation_obj = str(self._ids.objects.activation)
        activation_node = [c for c in path if c.get_type() == activation_obj]
        if activation_node != []:
            activation_node = activation_node
        else:
            activation_node = None
        mid_node = interaction
        edgelist = []
        for index,node in enumerate(path):
            if index >=2:
                if repression_obj == node.get_type():
                    if mid_node.get_type() == repression_obj:
                        if activation_node is not None:
                            mid_node = activation_node
                        mid_node = activation_obj
                    mid_node = node
                elif activation_obj == node.get_type():
                    if mid_node.get_type() != repression_obj:
                        activation_node = node
                        mid_node = node
            if index >= len(path) - 1:
                return mid_node,edgelist,node
            v_node = path[index+1]
            ret_val = self._graph.edge_query(n=node,v=v_node,
                                directed=False,exclusive=True)
            edgelist.append(ret_val[0].get_type())
        raise ValueError(f'Inputed path is empty.')

    def _reduce(self,l):
        seen = set()
        seen_add = seen.add
        return [x for x in l if not (x in seen or seen_add(x))]
        
    def _project(self,name,n,e):
        return self.project(name,n,e,
                nodeProperties=self._node_props(),
                relationshipProperties=self._edge_props(),
                validateRelationships=False)

    def _node_props(self):
        props = []
        for k,v in self._graph.get_node_properties().items():
            for k1,v1 in v.items():
                if is_num(v1):
                    props.append(k1)
        return list(set(props))

    def _edge_props(self):
        props = []
        for k,v in self._graph.get_edge_properties().items():
            for k1,v1 in v.items():
                if is_num(v1):
                    props.append(k1)
        return list(set(props))
    
    def _get_interaction_io(self,subject):
        inputs = []
        outputs = []
        d_predicate = self._graph.model.identifiers.predicates.direction
        i_predicate = self._graph.model.identifiers.objects.input
        o_predicate = self._graph.model.identifiers.objects.output
        for edge in self._graph.edge_query(n=subject):
            e_type = edge.get_type()
            model_code = self._graph.model.get_class_code(e_type)
            for d in [d[1] for d in self._graph.model.search((model_code,d_predicate,None))]:
                d,d_data = d
                if d_data["key"] == i_predicate:
                    inputs.append(edge)
                elif d_data["key"] == o_predicate:
                    outputs.append(edge)
                else:
                    raise ValueError(f'{labels} has direction not input or output')
        return inputs,outputs

    def _run(self,qry):
        return self._driver.run_cypher(qry)

def is_num(value):
    try:
        float(value)
        return True
    except Exception:
        try:
            int(value)
        except:
            return False

def _get_name(subject):
    split_subject = _split(str(subject))
    if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
        return split_subject[-2]
    else:
        return split_subject[-1]

def _split(uri):
    return re.split('#|\/|:', uri)