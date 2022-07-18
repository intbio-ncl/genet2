import random
import re
from string import ascii_lowercase

from app.graph.utility.model.model import model
from app.graph.utility.graph_objects.node import Node

presets = ["hierarchy",
"interaction",
"interaction_ppi",
"interaction_genetic"
]

class ProjectBuilder():
    def __init__(self, graph):
        self._graph = graph
        self._driver = self._graph.driver
        self._ids = model.identifiers
        self._procedures = self._graph.procedure

    def get_graph(self,name):
        return self._driver.project.get_graph(name)

    def get_presets(self):
        return presets
        
    def get_projected_names(self):
        return self._driver.project.names()

    def hierarchy(self,name,direction="NATURAL"):
        e = {self._ids.predicates.has_part:{"orientation" : direction}}
        n = []
        for edge in self._graph.get_haspart():
            n += [str(edge.n),str(edge.v)]
        n = self._cast(list(set(n)))
        return self._driver.project.cypher_project(name,n,e)

    def interaction(self,name,direction="DIRECTED",type="bipartite"):
        i_name = ''.join(random.choice(ascii_lowercase) for i in range(10))
        graph,ints,pet = self._interaction_direction(i_name,direction.upper())
        nodes = []
        edges = []
        if type.lower() == "bipartite":
            for int,(i,o) in ints.items():
                for inp in i:
                    nodes.append(inp.n)
                    nodes.append(inp.v)
                    edges.append(inp.get_type())
                for out in o:
                    nodes.append(out.n)
                    nodes.append(out.v)
                    edges.append(out.get_type())
            nodes = self._cast(nodes)
            graph = self._driver.project.sub_graph(i_name,name,nodes,edges)
        elif type.lower() == "monopartite":
            seens = []
            for interaction,(i,o) in ints.items():
                it = interaction.get_type()
                if it in seens:
                    continue
                seens.append(it)
                types = self._reduce([e.get_type() for e in i+o])
                self._driver.project.mutate(i_name,types,it)
            # Project Aggregation.
            graph = self._driver.project.sub_graph(i_name,name,pet,seens)
        self._driver.project.drop(i_name)
        return graph

    def interaction_ppi(self,name,direction="DIRECTED",type="monopartite"):
        i_name = ''.join(random.choice(ascii_lowercase) for i in range(10))
        graph,ints,pet = self._interaction_direction(i_name,direction.upper())
        p_obj = self._graph.get_protein()
        if type.lower() == "bipartite":
            graph = self._interaction_bipartite(graph,i_name,name,ints,p_obj)
        elif type.lower() == "monopartite":
            graph = self._interaction_monopartite(graph,i_name,name,ints,p_obj)
        self._driver.project.drop(i_name)
        return graph

    def interaction_genetic(self,name,direction="DIRECTED",type="monopartite"):
        i_name = ''.join(random.choice(ascii_lowercase) for i in range(10))
        graph,ints,pet = self._interaction_direction(i_name,direction.upper())
        dna_obj = self._graph.get_dna()
        if type.lower() == "bipartite":
            graph = self._interaction_bipartite(graph,i_name,name,ints,dna_obj)
        elif type.lower() == "monopartite":
            graph = self._interaction_monopartite(graph,i_name,name,ints,dna_obj)
        self._driver.project.drop(i_name)
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
        elif direction == "REVERSE":
            di = "NATURAL"
            do = "REVERSE"
        interactions = {i:self._graph.get_interaction_io(i) for i in self._graph.get_interaction()}
        for interaction,io in interactions.items():
            inps,outs = io
            nodes.append(interaction)
            for i in inps:
                nodes.append(i.v)
                pet.append(i.v.get_key())
                i = str(i.get_type())
                if i not in e:
                    e[i] = {"orientation" : di}
            for o in outs:
                nodes.append(o.v)
                pet.append(o.v.get_key())
                o = str(o.get_type())
                if o not in e:
                    e[o] = {"orientation" : do} 
        return self._driver.project.project(name,nodes,e)[0],interactions,list(set(pet))

    def _interaction_bipartite(self,graph,o_name,n_name,interactions,objs):
        int_map,objs = self._interaction(graph,interactions,objs)
        f_interactions = []
        seens = []
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
                if i_type not in seens:
                    self._driver.project.mutate(o_name,el1,i_type,node_labels=node_label)
                    seens.append(i_type)
                if o_type not in seens:
                    self._driver.project.mutate(o_name,el2,o_type,node_labels=i_node.get_key())
                    seens.append(o_type)
        graph = self._driver.project.sub_graph(o_name,n_name,objs,f_interactions)
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
                # Undirected graphs with path finding source == dest
                if len(path) == 2 and path[0] == path[1]:
                    continue
                i_type = self._unique_interaction_type(i_type,node_label,dest)
                f_interactions.append(i_type)
                r = self._driver.project.mutate(o_name,path,i_type,node_labels=node_label)
        # Project Aggregation.
        graph = self._driver.project.sub_graph(o_name,n_name,objs,f_interactions)
        return graph
    
    def _interaction(self,graph,interactions,objs):
        int_map = {}
        objects = list(set([i.v for int,(inps,outs) in interactions.items() 
                            for i in inps if i.v in objs]))
        for interaction,(inps,outs) in interactions.items():
            for i in inps:
                if i.v not in objects:
                    continue
                source = self._cast(i.n)
                os = [o.get_type() for o in objects]
                paths = self._driver.procedures.path_finding.dijkstra_sp(graph,source,os)
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
        return int_map,objects

    def _unique_interaction_type(self,i_type,source,dest):
        return i_type + f"/{_get_name(source)}/{_get_name(dest)}"

    def _derive_edgelist(self,interaction,path):
        '''
        Projections dont encode relationship labels but nodelists.
        Derives an edgelist from nodelist using persistent graph.
        Also calculates aggregated interaction type via walk.
        1. Start with input interaction type.
        2. If a repression interaction is found flip the return interaction type.
        Can return repression, activation or input interaction
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
            ret_val = self._graph.edges(n=node,v=v_node,directed=False,exclusive=True)
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
            ret_val = self._graph.edges(n=node,v=v_node,
                                directed=False,exclusive=True)
            edgelist.append(ret_val[0].get_type())
        raise ValueError(f'Inputed path is empty.')

    def _reduce(self,l):
        seen = set()
        seen_add = seen.add
        return [x for x in l if not (x in seen or seen_add(x))]

    def _cast(self,nodes):
        if not isinstance(nodes,list):
            nodes = [nodes]        
        for index in range(0,len(nodes)):
            node = nodes[index]
            if not isinstance(node,Node):
                node = Node(node,graph_name=self._graph.name)
            else:
                node.graph_name = self._graph.name

            nodes[index] = node
        return nodes
        
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