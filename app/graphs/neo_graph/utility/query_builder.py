from app.graphs.graph_objects.node import Node
from app.graphs.neo_graph.utility.operations import NodeOperations
from app.graphs.neo_graph.utility.operations import EdgeOperations

class Call:
    def __init__(self,procedure,name,mode):
        self.procedure = procedure
        self.name = name
        self.mode = mode

class StringBuilder:
    def __init__(self):
        self._matches = {}
        self._wheres = []
        self._parameters = {}
        self._call = None
        self._yields = []
        self._returns = []

    def MATCH(self,name,where):
        if isinstance(where,Node):
            where = [where.get_key()]
        if not isinstance(where,list):
            where = [where]
        self._matches[name] = where
        return self

    def CALL(self,procedure,name,mode):
        self._call = Call(procedure,name,mode)
        return self

    def PARAMETER(self,key,value):
        self._parameters[key] = value
        return self

    def YIELD(self,yields):
        if not isinstance(yields,list):
            yields = [yields]
        self._yields += yields
        return self
    
    def RETURN(self,val):
        if not isinstance(val,list):
            val = [val]
        self._returns += val
        return self

    def BUILD(self):
        f_str = ""
        for name,match in self._matches.items():
            f_str += f"MATCH ({name}) "
            if len(match) > 0:
                f_str += "WHERE " + " AND ".join([f"{name}:`" + str(s) + "`" for s in match])
        if self._call:
            f_str += f" CALL {self._call.procedure}.{self._call.mode}('{self._call.name}' {',' if len(self._parameters) > 0 else ''}"
        for index,(k,v) in enumerate(self._parameters.items()):
            if index == 0:
                f_str += "{"
            if isinstance(v,str) and v not in self._matches.keys():
                v = f'"{v}"'
            f_str += f'{k} : {v} '
            if index < len(self._parameters) - 1:
                f_str += ","
            if index >= len(self._parameters) - 1:
                f_str += "}"
        if self._call:
            f_str += ")"
        if len(self._yields) > 0:
            f_str += f' YIELD {",".join(self._yields)} '
        if len(self._returns) > 0:
            f_str += f' RETURN {",".join(self._returns)} '
        return f_str

    


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
        if isinstance(identity,Node):
            identity = [identity]
        if isinstance(identity, (list, tuple, set, frozenset)):
            where = "WHERE "
            for index, i in enumerate(identity):
                where += f'n:`{i}`'
                if index < len(identity) - 1:
                    where += " OR "
            identity = ""
        return f"""MATCH (n{":" + str(identity) if identity else ""} {{{self.dict_to_query(kwargs)}}}) {where} RETURN n"""

    def edge_query(self, n=None, v=None, e=None, n_props={}, v_props={}, e_props={},directed=True,exclusive=False):
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

        n,n_where = _cast_node(n,"n")
        v,v_where = _cast_node(v,"v")
        if isinstance(e, list):
            e = ":" + ""+"|".join(["`" + edge + "`" for edge in e])
        else:
            e = f':`{e}`' if e else ""

        n = f'(n{n} {{{self.dict_to_query(n_props)}}})'
        e = f'[e{e} {{{self.dict_to_query(e_props)}}}]'
        v = f'(v{v} {{{self.dict_to_query(v_props)}}})'
        where = f'{"WHERE" if n_where !="" or v_where != "" else ""} {n_where} {"AND" if n_where != "" and v_where != "" else ""} {v_where}'
        return f"""MATCH {n}-{e}-{">" if directed else ""}{v} {where} RETURN n,v,e"""

    def count_edges(self):
        return "MATCH (n)-[r]->() RETURN COUNT(r)"

    def get_property(self, n=None, prop=""):
        return f"""MATCH (p{":" + n if n else ""}) RETURN p.{prop}"""

    def get_labels(self):
        return "call db.labels()"
    
    def get_types(self):
        return "MATCH (n)-[r]-(m) RETURN distinct type(r)"
        
    def get_node_properties(self):
        return "MATCH (n) return properties(n)" 

    def get_edge_properties(self):
        return "MATCH (n)-[r]-(m) RETURN properties(r)"

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

    def cypher_project(self,name,nodes=None,edges=None):
        def _where(n):
            where = ""
            if n is not None:
                if not isinstance(n,list):
                    n = [n]
                where = ""
                w_inner = ""
                v_inner = ""
                for index, i in enumerate(n):
                    if index == 0:
                        where = " WHERE "
                    w_inner += f'n:`{i}`'
                    v_inner += f'v:`{i}`'
                    if index < len(n) - 1:
                        w_inner += " OR "
                        v_inner += " OR "
                return f'{where} {w_inner} {"AND" if len(w_inner+v_inner)>0 else ""} {v_inner}'
            return where
        
        ewhere = _where(nodes)
        e = ""
        if edges is not None and len(edges) > 0:
            e = ":" + "" + ""+"|".join(["`" + str(edge) + "`" for edge in edges])
            
        n_str = f"MATCH (n)-[r{e}]-(v) {ewhere} RETURN id(n) AS id"
        e_str = f"MATCH (n)-[r{e}]->(v) {ewhere} RETURN id(n) AS source, id(v) AS target"
        return f'''
        CALL gds.graph.project.cypher(
        '{name}',
        '{n_str}',
        '{e_str}',
         {{validateRelationships: false}}   )
        YIELD graphName AS graph, nodeQuery, nodeCount AS nodes, relationshipQuery, relationshipCount AS rels
        '''


    def mutate(self,name,types,mutate_type,node_labels=None):
        sb = StringBuilder()
        sb.CALL("gds.alpha.collapsePath",name,"mutate")
        sb.PARAMETER("relationshipTypes",types)
        sb.PARAMETER("mutateRelationshipType",mutate_type)
        sb.PARAMETER("allowSelfLoops",False)
        if node_labels:
            sb.PARAMETER("nodeLabels",node_labels)
        sb.YIELD("relationshipsWritten")
        return sb.BUILD()

    def page_rank(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.pageRank",name,mode)
        sb.YIELD(["nodeId","score"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "score"])
        return sb.BUILD()

    def article_rank(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.articleRank",name,mode)
        sb.YIELD(["nodeId","score"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "score"])
        return sb.BUILD()

    def eigenvector_centrality(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.eigenvector",name,mode)
        sb.YIELD(["nodeId","score"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "score"])
        return sb.BUILD()

    def betweenness_centrality(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.betweenness",name,mode)
        sb.YIELD(["nodeId","score"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "score"])
        return sb.BUILD()

    def degree_centrality(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.degree",name,mode)
        sb.YIELD(["nodeId","score"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "score"])
        return sb.BUILD()

    def closeness_centrality(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.beta.closeness",name,mode)
        sb.YIELD(["nodeId","score"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "score"])
        return sb.BUILD()

    def harmonic_centrality(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.alpha.closeness.harmonic",name,mode)
        sb.YIELD(["nodeId","centrality"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "centrality"])
        return sb.BUILD()

    def hits(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.alpha.hits",name,mode)
        sb.PARAMETER("hitsIterations", 20)
        sb.YIELD(["nodeId","values"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "values"])
        return sb.BUILD()

    def celf_influence_maximization(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.alpha.influenceMaximization.celf",name,mode)
        sb.PARAMETER("seedSetSize", 3)
        sb.YIELD(["nodeId","spread"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "spread"])
        return sb.BUILD()

    def greedy_influence_maximization(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.alpha.influenceMaximization.greedy",name,mode)
        sb.PARAMETER("seedSetSize", 3)
        sb.YIELD(["nodeId","spread"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "spread"])
        return sb.BUILD()

    def louvain(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.louvain",name,mode)
        sb.YIELD(["nodeId","communityId","intermediateCommunityIds"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "communityId","intermediateCommunityIds"])
        return sb.BUILD()

    def label_propagation(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.labelPropagation",name,mode)
        sb.YIELD(["nodeId","communityId"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "communityId"])
        return sb.BUILD()
    
    def wcc(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.wcc",name,mode)
        sb.YIELD(["nodeId","componentId"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "componentId"])
        return sb.BUILD()

    def triangle_count(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.triangleCount",name,mode)
        sb.YIELD(["nodeId","triangleCount"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "triangleCount"])
        return sb.BUILD()

    def local_clustering_coefficient(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.localClusteringCoefficient",name,mode)
        sb.YIELD(["nodeId","localClusteringCoefficient"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "localClusteringCoefficient"])
        return sb.BUILD()

    def k1coloring(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.beta.k1coloring",name,mode)
        sb.YIELD(["nodeId","color"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "color"])
        return sb.BUILD()

    def modularity_optimization(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.beta.modularityOptimization",name,mode)
        sb.YIELD(["nodeId","communityId"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "communityId"])
        return sb.BUILD()
    
    def scc(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.alpha.scc",name,mode)
        sb.YIELD(["nodeId","componentId"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "componentId"])
        return sb.BUILD()

    def sllpa(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.alpha.sllpa",name,mode)
        sb.PARAMETER("maxIterations", 100)
        sb.YIELD(["nodeId","values"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "values.communityIds AS communityIds"])
        return sb.BUILD()
    
    def maxkcut(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.alpha.maxkcut",name,mode)
        sb.YIELD(["nodeId","communityId"])
        sb.RETURN(["gds.util.asNode(nodeId) AS node", "communityId"])
        return sb.BUILD()

    def node_similarity(self,name,mode="stream"):
        sb = StringBuilder()
        sb.CALL("gds.nodeSimilarity",name,mode)
        sb.YIELD(["node1", "node2", "similarity"])
        sb.RETURN(["gds.util.asNode(node1) AS node1", 
                   "gds.util.asNode(node2) AS node2", "similarity"])
        return sb.BUILD()

    def knn(self,name,node_properties,mode="stream"):
        if not isinstance(node_properties,list):
            node_properties = [node_properties]
        sb = StringBuilder()
        sb.CALL("gds.knn",name,mode)
        sb.PARAMETER("nodeProperties",str(node_properties))
        sb.PARAMETER("topK",1)
        sb.PARAMETER("randomSeed",1337)
        sb.PARAMETER("concurrency",1)
        sb.PARAMETER("sampleRate",1.0)
        sb.PARAMETER("deltaThreshold",0.0)
        sb.YIELD(["node1", "node2", "similarity"])
        sb.RETURN(["gds.util.asNode(node1) AS node1", 
                   "gds.util.asNode(node2) AS node2", "similarity"])
        return sb.BUILD()

    def delta_all_shortest_paths(self,name,source,mode="stream"):
        sb = StringBuilder()
        sb.MATCH("source",source)
        sb.CALL("gds.allShortestPaths.delta",name,mode)
        sb.PARAMETER("sourceNode", "source")
        sb.YIELD(["totalCost","path"])
        sb.RETURN(["totalCost","nodes(path) as path"])
        return sb.BUILD()

    def dijkstra_all_shortest_paths(self,name,source,mode="stream"):
        sb = StringBuilder()
        sb.MATCH("source",source)
        sb.CALL("gds.allShortestPaths.dijkstra",name,mode)
        sb.PARAMETER("sourceNode", "source")
        sb.YIELD(["totalCost","path"])
        sb.RETURN(["totalCost","nodes(path) as path"])
        return sb.BUILD()

    def dijkstra_shortest_path(self,name,source,dest,mode="stream"):
        sb = StringBuilder()
        sb.MATCH("source",source)
        sb.MATCH("dest",dest)
        sb.CALL("gds.shortestPath.dijkstra",name,mode)
        sb.PARAMETER("sourceNode", "source")
        sb.PARAMETER("targetNode","dest")
        sb.YIELD(["totalCost","path"])
        sb.RETURN(["totalCost","nodes(path) as path"])
        return sb.BUILD()

    def astar_shortest_path(self,name,source,dest,latitude_property,
                            longitude_property,mode="stream"):
        sb = StringBuilder()
        sb.MATCH("source",source)
        sb.MATCH("dest",dest)
        sb.CALL("gds.shortestPath.astar",name,mode)
        sb.PARAMETER("sourceNode", "source")
        sb.PARAMETER("targetNode","dest")
        sb.PARAMETER("latitudeProperty",latitude_property)
        sb.PARAMETER("longitudeProperty",longitude_property)
        sb.YIELD(["totalCost","path"])
        sb.RETURN(["totalCost","nodes(path) as path"])
        return sb.BUILD()

    def yens_shortest_path(self,name,source,dest,k,mode="stream"):
        sb = StringBuilder()
        sb.MATCH("source",source)
        sb.MATCH("dest",dest)
        sb.CALL("gds.shortestPath.yens",name,mode)
        sb.PARAMETER("sourceNode", "source")
        sb.PARAMETER("targetNode","dest")
        sb.PARAMETER("k",k)
        sb.YIELD(["totalCost","path"])
        sb.RETURN(["totalCost","nodes(path) as path"])
        return sb.BUILD()

    def dfs(self,name,source,dest,mode="stream"):
        sb = StringBuilder()
        sb.MATCH("source",source)
        sb.MATCH("dest",dest)
        sb.CALL("gds.dfs",name,mode)
        sb.PARAMETER("sourceNode", "source")
        sb.PARAMETER("targetNodes","dest")
        sb.YIELD("path")
        sb.RETURN("path")
        return sb.BUILD()

    def bfs(self,name,source,dest,mode="stream"):
        sb = StringBuilder()
        sb.MATCH("source",source)
        sb.MATCH("dest",dest)
        sb.CALL("gds.bfs",name,mode)
        sb.PARAMETER("sourceNode", "source")
        sb.PARAMETER("targetNodes","dest")
        sb.YIELD("path")
        sb.RETURN("path")
        return sb.BUILD()

    def adamic_adar(self,name,node1,node2):
        sb = StringBuilder()
        sb.MATCH("n1",node1)
        sb.MATCH("n2",node2)
        sb.RETURN(f"gds.alpha.linkprediction.adamicAdar('{name}',n1, n2) AS score")
        return sb.BUILD()

    def subgraph(self,o_name,n_name,nodes,edges):
        if len(nodes) == 0:
            node = "*"
        else:
            node =  "n:" + " OR n:".join([f'`{n}`' for n in nodes])
        if len(edges) == 0:
            edge = "*"
        else:
            edge = "r:" + " OR r:".join([f'`{e}`' for e in edges])
        return f'''
        CALL gds.beta.graph.project.subgraph(
        '{n_name}',
        '{o_name}',
        '{node}',
        '{edge}'
        )
        YIELD graphName, fromGraphName, nodeCount, relationshipCount
        '''
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