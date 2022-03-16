import json
import networkx as nx
from rdflib import Literal,URIRef

accepted_file_types = ['json']
def convert(input_fn,model_graph):
    graph = nx.MultiDiGraph()
    
    with open(input_fn) as f:
        js_graph = json.load(f)

    for node in js_graph["nodes"]:
        if "id" not in node.keys():
            continue
        n_id = node["id"]
        key = node["key"]
        if node["type"] == "URI":
            key = URIRef(key)
        else:
            key = Literal(key)
        del node["id"]
        del node["key"]
        del node["type"]
        graph.add_node(n_id,key=key,**node)      

    for edge in js_graph["links"]:
        source = edge["source"]
        target = edge["target"]
        key = URIRef(edge["key"])
        del edge["source"]
        del edge["target"]
        del edge["key"]
        graph.add_edge(source,target,key=key,**edge)
    return graph