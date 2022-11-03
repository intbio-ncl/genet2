from  app.graph.utility.graph_objects.node import Node

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
                f_str += "WHERE "
                for index, i in enumerate(match):
                    if i is None:
                        continue
                    if isinstance(i,Node):
                        f_str += f'{name}:`{i.get_key()}`' if i.get_key() != "None" else ""
                        f_str += f' AND {name}:`{i.get_type()}`' if i.get_type() != "None" else ""
                        f_str += f' AND ANY(a IN {str(i.graph_name)} WHERE a IN {name}.`graph_name`)'
                    else:
                        f_str += f'{name}:`{i}`'                        
                    if index < len(match) - 1:
                        f_str += " OR "

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

class GDSQueryBuilder:
    def __init__(self):
        pass
        
    def cypher_project(self,name,nodes=None,edges=None):
        where = " WHERE "
        def _where(n):    
            if n is not None:
                if not isinstance(n,list):
                    n = [n]
                w_inner = ""
                v_inner = ""
                for index, i in enumerate(n):
                    if isinstance(i,Node):
                        w_inner += f' (n:`{i.get_key()}`' if i.get_key() != "None" else ""
                        w_inner += f' AND n:`{i.get_type()}`' if i.get_type() != "None" else ""
                        w_inner += f' AND ANY(a IN {str(i.graph_name)} WHERE a IN n.`graph_name`)) '

                        v_inner += f'  (v:`{i.get_key()}`' if i.get_key() != "None" else ""
                        v_inner += f' AND v:`{i.get_type()}`' if i.get_type() != "None" else ""
                        v_inner += f' AND ANY(a IN {str(i.graph_name)} WHERE a IN v.`graph_name`)) '
                    else:
                        w_inner += f'( n:`{i}` )'
                        v_inner += f' (v:`{i}` )'   
                    if index < len(n) - 1:
                        w_inner += " OR "
                        v_inner += " OR "
                print(len(w_inner+v_inner)>0)
                return f'{where} {w_inner} {"AND" if len(w_inner+v_inner)>0 else ""} {v_inner} '
            return where
        
        ewhere = _where(nodes)
        all_gns = list(set([item for sublist in nodes for item in sublist.graph_name]))
        e = ""
        if edges is not None and len(edges) > 0:
            e = ":" + "" + ""+"|".join(["`" + str(edge) + "`" for edge in edges])
        
        gnwhere = f'{"AND" if len(ewhere) != where else ""} ANY(a IN {str(all_gns)} WHERE a IN r.`graph_name`)' if len(ewhere)+len(nodes)>0 else ''
        n_str = f"MATCH (n)-[r{e}]-(v) {ewhere}  {gnwhere} RETURN id(n) AS id, labels(n) AS labels"
        e_str = f"MATCH (n)-[r{e}]->(v) {ewhere} {gnwhere} RETURN id(n) AS source, id(v) AS target, type(r) AS type"
        return f'''
        CALL gds.graph.project.cypher(
        "{name}",
        "{n_str}",
        "{e_str}",
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

    def dfs(self,name,source,dest=None,mode="stream"):
        sb = StringBuilder()
        sb.MATCH("source",source)
        if dest is not None:
            sb.MATCH("dest",dest)
        sb.CALL("gds.dfs",name,mode)
        sb.PARAMETER("sourceNode", "source")
        if dest is not None:
            sb.PARAMETER("targetNodes","dest")
        sb.YIELD("path")
        sb.RETURN("path")
        return sb.BUILD()

    def bfs(self,name,source,dest=None,mode="stream"):
        sb = StringBuilder()
        sb.MATCH("source",source)
        if dest is not None:
            sb.MATCH("dest",dest)
        sb.CALL("gds.bfs",name,mode)
        sb.PARAMETER("sourceNode", "source")
        if dest is not None:
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