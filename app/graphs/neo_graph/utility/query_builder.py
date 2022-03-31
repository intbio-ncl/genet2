from app.graphs.graph_objects.node import Node
from app.graphs.neo_graph.utility.operations import NodeOperations
from app.graphs.neo_graph.utility.operations import EdgeOperations

class QueryBuilder:
    def __init__(self):
        self.index = 1
        self.nodes = {}
        self.edges = {}
        

    def is_node_staged(self, n):
        return n in self.nodes

    def update_node(self, node):
        pass

    def is_edge_staged(self, edge):
        return edge in self.edges

    def update_edge(self, edge):
        #n2 = self.staged_nodes[node]
        # n2.update(node)
        pass

    def add_create_node(self, node):
        self._add_node(node)
        self.nodes[node].enable_create()

    def add_create_edge(self, edge):
        self._add_edge(edge)
        self.edges[edge].enable_create()

    def add_match_node(self, node):
        self._add_node(node)
        self.nodes[node].enable_match()
    
    def add_match_edge(self, edge):
        self._add_edge(edge)
        self.edges[edge].enable_match()

    def add_set_node(self, node,new_props):
        self._add_node(node)
        self.nodes[node].enable_set(new_props)

    def add_set_edge(self, edge,new_props):
        self._add_edge(edge)
        self.edges[edge].enable_set(new_props)

    def add_replace_node_properties(self, node,new_props):
        self._add_node(node)
        self.nodes[node].use_properties = False
        self.nodes[node].enable_replace_properties(new_props)

    def add_replace_edge_properties(self,edge,new_props):
        self._add_edge(edge)
        self.edges[edge].use_properties = False
        self.edges[edge].enable_replace_properties(new_props)

    def add_remove_node(self, node):
        self._add_node(node)
        self.nodes[node].enable_remove()

    def add_remove_edge(self, edge):
        self._add_edge(edge)
        self.edges[edge].enable_remove()

    def add_remove_node_property(self,node,properties):
        self._add_node(node)
        self.nodes[node].use_properties = False
        self.nodes[node].enable_remove_properties(properties)

    def add_remove_edge_property(self,edge,properties):
        self._add_edge(edge)
        self.edges[edge].use_properties = False
        self.edges[edge].enable_remove_properties(properties)

    def generate(self):
        for operation in self.nodes.values():
            yield operation.generate()
        for operation in self.edges.values():
            yield operation.generate()
        self.nodes.clear()
        self.edges.clear()
        self.index = 1
        
    def purge(self):
        return "MATCH (n) DETACH DELETE n"

    def node_query(self, identity, **kwargs):
        where = ""
        if isinstance(identity, (list, tuple, set, frozenset)):
            where = "WHERE "
            for index, i in enumerate(identity):
                where += f'n:`{i}`'
                if index < len(identity) - 1:
                    where += " OR "
            identity = ""
        return f"""MATCH (n{":" + str(identity) if identity else ""} {{{self.dict_to_query(kwargs)}}}) {where} RETURN n"""

    def edge_query(self, n=None, v=None, e=None, n_props={}, v_props={}, e_props={}):
        where = ""
        if isinstance(n, Node):
            n = ":" + str(n)
        elif isinstance(n, (list, tuple, set)):
            where = "WHERE"
            for index,node in enumerate(n):
                if isinstance(node,Node):
                    where += f'n:{node}'
                else:
                    where += f'n:`{node}`'
                if index < len(n) -1:
                    where += " OR "
            n = ""
        else:
            n = ":`"+n+"`" if n else ""

        if isinstance(v, Node):
            v = ":" + str(v)
        elif isinstance(v, (list, tuple, set)):
            where += "WHERE " if where == "" else " OR "
            for index,node in enumerate(v):
                if isinstance(node,Node):
                    where += f'v:{node} '
                else:
                    where += f'v:`{node}` '
                if index < len(v) -1:
                    where += " OR "
            v = ""
        else:
            v = ":`"+v+"`" if v else ""

        if isinstance(e, list):
            e = ":" + ""+"|".join(["`" + edge + "`" for edge in e])
        else:
            e = f':`{e}`' if e else ""

        n = f'(n{n} {{{self.dict_to_query(n_props)}}})'
        e = f'[e{e} {{{self.dict_to_query(e_props)}}}]'
        v = f'(v{v} {{{self.dict_to_query(v_props)}}})'
        return f"""MATCH {n}-{e}->{v} {where} RETURN n,v,e"""

    def count_edges(self):
        return "MATCH (n)-[r]->() RETURN COUNT(r)"

    def get_property(self, n=None, prop=""):
        return f"""MATCH (p{":" + n if n else ""}) RETURN p.{prop}"""

    def shortest_path(self, source, dest):
        if isinstance(source, Node):
            source = source.labels
        elif not isinstance(source, (list, set, tuple)):
            source = [source]
        if isinstance(dest, Node):
            dest = dest.labels
        elif not isinstance(dest, (list, set, tuple)):
            dest = [dest]
        return f"""
        MATCH (a:{self.list_to_query(source)}),(b:{self.list_to_query(dest)}),
        p = shortestPath((a)-[*]-(b))
        RETURN p
        """

    def degree(self, source, **kwargs):
        return f"""MATCH (p:{self.list_to_query(source)} {{{self.dict_to_query(kwargs)}}})
                   RETURN apoc.node.degree(p) AS output"""

    def is_dense(self, source, **kwargs):
        return f"""MATCH (p:{self.list_to_query(source)} {{{self.dict_to_query(kwargs)}}})
                   RETURN apoc.nodes.isDense(p) AS output"""

    def cycles(self, source, **kwargs):
        return f"""MATCH (m1:{self.list_to_query(source)} {{{self.dict_to_query(kwargs)}}}) 
                    WITH collect(m1) as nodes CALL apoc.nodes.cycles(nodes) YIELD path RETURN path"""

    def is_connected(self, n, v, n_props={}, v_props={}):
        return f"""
        MATCH (p1:{self.list_to_query(n)} {{{self.dict_to_query(n_props)}}}) 
        MATCH (p2:{self.list_to_query(v)} {{{self.dict_to_query(v_props)}}}) 
        RETURN apoc.nodes.connected(p1, p2) AS output;"""

    def collapse(self, n=None, v=None, edges=[], n_props={}, v_props={}):
        n_str = f"p {':' + '`'+ self.list_to_query(n) +'`' if n else ''}  {{{self.dict_to_query(n_props)}}}"
        v_str = f"c {':' + '`'+ self.list_to_query(v) +'`' if v else ''} {{{self.dict_to_query(v_props)}}}"
        e_str = f":{'|'.join([f'`{e}`' for e in edges])}" if len(
            edges) > 0 else "*"
        return f"""
        MATCH ({n_str})-[{e_str}]->({v_str})
        WITH c, collect(p) as subgraph
        CALL apoc.nodes.collapse(subgraph,{{properties:'combine'}})
        YIELD from, rel, to
        RETURN from, rel, to;"""

    def k_spanning_tree(self, source, edge_filters=None, max_level=-1, **kwargs):
        edge_filters = 'relationshipFilter:"' + \
            "|".join([f'`{e}`' for e in edge_filters]) + \
            '",' if edge_filters else ""
        return f"""
        MATCH (p:{self.list_to_query(source)} {{{self.dict_to_query(kwargs)}}}) 
        CALL apoc.path.spanningTree(p, {{
            {edge_filters}
            minLevel: 1,
            maxLevel: {str(max_level)}
        }})
        YIELD path
        RETURN path"""

    def dict_to_query(self, items):
        f_str = ""
        for index, (k, v) in enumerate(items.items()):
            v = v if isinstance(v, list) else f'"{v}"'
            f_str += f'`{k}`: {v}'
            if index != len(items) - 1:
                f_str += ","
        return f_str

    def list_to_query(self, items):
        f_str = ""
        for index, item in enumerate(items):
            f_str += f'`{item}`'
            if index < len(items) - 1:
                f_str += ":"
        return f_str

    def _add_node(self,node):
        if node not in self.nodes:
            no = NodeOperations(node,self.index)
            self.nodes[node] = no
        self.index += 1

    def _add_edge(self,edge):
        if edge.n not in self.nodes:
            self._add_node(edge.n)
        if edge.v not in self.nodes:
            self._add_node(edge.v)
        n_index = self.nodes[edge.n].index
        v_index = self.nodes[edge.v].index
        if edge not in self.edges:
            no = EdgeOperations(edge,self.index,n_index,v_index)
            self.edges[edge] = no
        self.index += 1