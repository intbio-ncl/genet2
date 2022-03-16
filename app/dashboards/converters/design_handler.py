import networkx as nx
from converters.design import sbol_convert
from converters.design import nv_convert
from converters.design import gbk_convert
from graph.design import DesignGraph

convert_dict = {"sbol" : sbol_convert,
                "gbk"  : gbk_convert,
                "nv"   : nv_convert}

def convert(model_graph,filename=None,convert_type=None):
    if filename is None:
        return DesignGraph(nx.MultiDiGraph())
    if convert_type is None:
        convert_type = derive_convert_type(filename)
    graph = convert_dict[convert_type].convert(filename,model_graph)
    return DesignGraph(graph)

def get_converter_names():
    return list(convert_dict.keys())
    
def derive_convert_type(filename):
    if filename.lower().endswith(tuple(v.lower() for v in sbol_convert.accepted_file_types)):
        return "sbol"
    elif filename.lower().endswith(tuple(v.lower() for v in gbk_convert.accepted_file_types)):
        return 'gbk'
    elif filename.lower().endswith(tuple(v.lower() for v in nv_convert.accepted_file_types)):
        return "nv"