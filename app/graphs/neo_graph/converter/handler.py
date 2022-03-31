from app.graphs.neo_graph.converter.design import sbol_convert
convert_dict = {"sbol" : sbol_convert}

def convert(graph,filename,mode,graph_name):
    convert_type = derive_convert_type(filename)
    convert_dict[convert_type].convert(filename,graph,mode,graph_name)

def get_converter_names():
    return list(convert_dict.keys())
    
def derive_convert_type(filename):
    if filename.lower().endswith(tuple(v.lower() for v in sbol_convert.accepted_file_types)):
        return "sbol"