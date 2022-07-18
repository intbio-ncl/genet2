from  app.graph.utility.graph_objects.node import Node
from  app.graph.neo4j_interface.operations import NodeOperations
from  app.graph.neo4j_interface.operations import EdgeOperations

class QueryBuilder:
    def __init__(self):
        self.index = 1
        self.nodes = {}
        self.edges = {}
        
    def is_node_staged(self, n):
        return n in self.nodes

    def is_edge_staged(self, edge):
        return edge in self.edges

    def add_create_node(self, node):
        self._add_node(node)
        self.nodes[node].enable_create()

    def add_create_edge(self, edge):
        self._add_edge(edge)
        self.edges[edge].enable_create()

    def add_match_node(self, node,use_id=False):
        self._add_node(node)
        self.nodes[node].enable_match(use_id)
    
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

    def add_add_node_label(self,node,label):
        self._add_node(node)
        self.nodes[node].enable_add_label(label)

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

    def node_query(self, identity,predicate="ALL", **kwargs):
        where = ""
        if not isinstance(identity,(list, tuple, set, frozenset)):
            identity = [identity]

        for index, i in enumerate(identity):
            if i is None:
                continue
            where += f'n:`{i}`'
            if index < len(identity) - 1:
                where += " OR "
        where = self._graph_name(kwargs,where,"n",predicate)
        if where != "":
            where = "WHERE " + where
        return f"""MATCH (n {{{self.dict_to_query(kwargs)}}}) {where} RETURN n"""

    def edge_query(self, n=None, v=None, e=None, n_props={}, v_props={}, 
                    e_props={},directed=True,exclusive=False,predicate="ALL"):
        return f"""{self._edge_match(n,v,e,n_props,v_props,e_props,directed,exclusive,predicate)} RETURN n,v,e"""

    def node_property(self, n=None, prop="",distinct=False):
        return f"""MATCH (p{":" + n if n else ""}) RETURN {"DISTINCT" if distinct else ""} p.{prop}"""
            
    def get_node_properties(self):
        return "MATCH (n) return properties(n)" 

    def get_edge_properties(self):
        return "MATCH (n)-[r]-(m) RETURN properties(r)"

    def get_isolated_nodes(self,identity=[],**kwargs):
        where = ""
        for index, i in enumerate(identity):
            if i is None:
                continue
            where += f'n:`{i}`'
            if index < len(identity) - 1:
                where += " OR "

        where = self._graph_name(kwargs,where,"n","ALL")
        return f'''
        match (n {{{self.dict_to_query(kwargs)}}})
        with n
        optional match (n)-[r]-()
        with n, count(r) as c
        where c=0 {"AND " + where if where != "" else ""}
        RETURn n
        '''

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

    def merge_relationship_nodes(self,edge):
        return f'''
        {self._edge_match(n=edge.n,v=edge.v,e=edge.get_type(),e_props=edge.get_properties())}
        CALL apoc.refactor.mergeNodes([n,v],{{properties:"combine",
                                                        mergeRels:TRUE,
                                                        produceSelfRel:FALSE,
                                                        preserveExistingSelfRels:FALSE}})
        YIELD node
        RETURN node
        '''

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
        items = {k:v for k,v in items.items() if k != "graph_name"}
        f_str = ""
        for index, (k, v) in enumerate(items.items()):
            if not isinstance(v,list):
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

    def _graph_name(self,kwargs,where,code,intersection):
        if "graph_name" in kwargs:
            gn = kwargs["graph_name"]
            if None in gn:
                return where
            if not isinstance(gn,list):
                gn = [gn]
            if where != "":
                where = f"({where}) AND "
            where += f"{intersection}(a IN {str(gn)} WHERE a IN {code}.`graph_name`)"
        return where

    def _edge_match(self, n=None, v=None, e=None, n_props={}, v_props={}, 
                    e_props={},directed=True,exclusive=False,predicate="ALL"):
        def _cast_node(n,code):
            where = ""
            if isinstance(n, Node):
                n = [n]
            if isinstance(n, (list, tuple, set)):
                where = ""
                for index,node in enumerate(n):
                    where += f'{code}:`{node}`'
                    if index < len(n) -1:
                        where += " OR " if not exclusive else " AND "
                n = ""
            else:
                n = ":`"+n+"`" if n else ""

            return n,where
        if n is not None and isinstance(n,Node):
            n_props.update(n.get_properties())
        if v is not None and isinstance(v,Node):
            v_props.update(v.get_properties())
        if e is not None and isinstance(e,Node):
            e_props.update(e.get_properties())
        n,n_where = _cast_node(n,"n")
        v,v_where = _cast_node(v,"v")
        n_where = self._graph_name(n_props,n_where,"n",predicate)
        v_where = self._graph_name(v_props,v_where,"v",predicate)
        e_where = self._graph_name(e_props,"","e",predicate)

        if isinstance(e, list):
            e = ":" + ""+"|".join(["`" + edge + "`" for edge in e])
        else:
            e = f':`{e}`' if e else ""

        n = f'(n{n} {{{self.dict_to_query(n_props)}}})'
        e = f'[e{e} {{{self.dict_to_query(e_props)}}}]'
        v = f'(v{v} {{{self.dict_to_query(v_props)}}})'
        where = n_where
        if v_where != "":
            if where != "":
                where += " AND "
            where += v_where
        if e_where != "":
            if where != "":
                where += " AND "
            where += e_where
        if where != "":
            where = "WHERE " + where

        return f'MATCH {n}-{e}-{">" if directed else ""}{v} {where}'