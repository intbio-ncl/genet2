from app.graph.graph_objects.node import Node


class QueryBuilder:
    def __init__(self):
        self.index = 1
        self.existing_nodes = {}
        self.staged_nodes = {}
        self.existing_edges = {}
        self.staged_edges = {}
        self.update_nodes = []
        self.update_edges = []
        self.removals = []

    def add_node(self, node):
        self.staged_nodes[node] = self.index
        self.index += 1

    def is_node_staged(self, n):
        return n in self.staged_nodes

    def add_existing_node(self, node):
        self.existing_nodes[node] = self.index
        self.index += 1

    def update_node(self, node):
        pass
        #n2 = self.staged_nodes[node]
        # n2.update(node)

    def add_node_update(self, node):
        self.update_nodes.append(node)

    def add_edge(self, edge):
        self.staged_edges[edge] = self.index
        self.index += 1

    def is_edge_staged(self, edge):
        return edge in self.staged_edges

    def update_edge(self, edge):
        #n2 = self.staged_nodes[node]
        # n2.update(node)
        pass

    def add_edge_update(self, edge):
        self.update_edges.append(edge)

    def add_existing_edge(self, edge):
        self.existing_edges[edge] = self.index
        self.index += 1

    def add_remove(self, item):
        self.removals.append(item)

    def generate_node(self, node, index):
        qry_str = f'(n{index}:{self.list_to_query(node.get_labels())} {{'
        qry_str += f'{ self.dict_to_query(node.get_properties())}'
        qry_str += '})'
        return qry_str

    def generate_edge(self, edge, index):
        def _derive_node(node):
            if node in self.staged_nodes:
                return self.staged_nodes[node]
            elif edge.v in self.existing_nodes:
                return self.existing_nodes[node]
        n = _derive_node(edge.n)
        v = _derive_node(edge.v)
        return f"""(`n{n}`)-[r{index}:{self.list_to_query(edge.get_labels())} {{{self.dict_to_query(edge.get_properties())}}}]->(`n{v}`)"""

    def generate_node_match(self, node, index):
        where = "WHERE "
        labels = node.get_labels()
        for c_index, i in enumerate(labels):
            where += f'n{index}:`{i}`'
            if c_index < len(labels) - 1:
                where += " OR "
        return f"""MATCH (n{index} {{{self.dict_to_query(node.get_properties())}}}) {where}\n"""

    def generate_update_node(self, n):
        set = "SET "
        index = self.existing_nodes[n]
        n_id = f'n{index}'
        props = n.get_properties()
        for c_index, (k, v) in enumerate(props.items()):
            set += f'{n_id}.`{k}` = "{v}"'
            if c_index < len(props) - 1:
                set += ", "
            else:
                set += "\n"
        return set

    def generate_edge_match(self, edge, index):
        n = ":" + str(edge.n)
        v = ":" + str(edge.v)
        e = ":" + ""+"|".join(["`" + e + "`" for e in edge.get_labels()])
        n = f'(n{n} {{{self.dict_to_query(edge.n.get_properties())}}})'
        e = f'[e{index}{e} {{{self.dict_to_query(edge.get_properties())}}}]'
        v = f'(v{v} {{{self.dict_to_query(edge.v.get_properties())}}})'
        return f"""MATCH {n}-{e}->{v}\n"""

    def generate_update_edge(self, n):
        set = "SET "
        index = self.existing_edges[n]
        n_id = f'e{index}'
        props = n.get_properties()
        for c_index, (k, v) in enumerate(props.items()):
            set += f'{n_id}.`{k}` = "{v}"'
            if c_index < len(props) - 1:
                set += ", "
            else:
                set += "\n"
        return set

    def generate_removal(self, item):
        if item in self.existing_nodes:
            return f'SET n{self.existing_nodes[item]} = {{{ self.dict_to_query(item.get_properties())}}} \n'
        if item in self.existing_edges:
            return f'SET e{self.existing_edges[item]} = {{{self.dict_to_query(item.get_properties())}}}\n'

    def generate(self):
        qry_str = ""
        if (len(self.staged_nodes) + len(self.staged_edges) +
           len(self.update_nodes) + len(self.update_edges) +
           len(self.removals) == 0):
            return qry_str

        for node, index in self.existing_nodes.items():
            if (node in self.staged_nodes
            or node in self.update_nodes
            or node in self.removals):
                qry_str += self.generate_node_match(node, index)

        for edge, index in self.existing_edges.items():
            if (edge in self.staged_edges 
            or edge in self.update_edges 
            or edge in self.removals):
                qry_str += self.generate_edge_match(edge, index)

        for node in self.update_nodes:
            qry_str += self.generate_update_node(node)

        for edge in self.update_edges:
            qry_str += self.generate_update_edge(edge)

        for r in self.removals:
            qry_str += self.generate_removal(r)

        if len(self.staged_nodes) + len(self.staged_edges) > 0:
            qry_str += "CREATE "
            for iter_index, (node, index) in enumerate(self.staged_nodes.items()):
                qry_str += self.generate_node(node, index)
                if iter_index < len(self.staged_nodes) - 1:
                    qry_str += ","
                qry_str += "\n"

            if len(self.staged_edges) > 0 and len(self.staged_nodes) > 0:
                qry_str += ","
            for iter_index, (edge, index) in enumerate(self.staged_edges.items()):
                qry_str += self.generate_edge(edge, index)
                if iter_index < len(self.staged_edges) - 1:
                    qry_str += ","
                qry_str += "\n"

        self.existing_nodes.clear()
        self.existing_edges.clear()
        self.staged_edges.clear()
        self.staged_nodes.clear()
        self.update_nodes.clear()
        self.update_edges.clear()
        self.removals.clear()
        self.index = 1
        return qry_str

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
            where = f'WHERE {"n:".join(["`" + node + "` OR" for node in n])}'
            n = ""
        else:
            n = ":`"+n+"`" if n else ""

        if isinstance(v, Node):
            v = ":" + str(v)
        elif isinstance(v, (list, tuple, set)):
            where += "WHERE " if where == "" else " OR "
            for index, node in enumerate(v):
                where += f'v:`{node}`'
                if index < len(v) - 1:
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
            f_str += f'`{k}`:"{v}"'
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
