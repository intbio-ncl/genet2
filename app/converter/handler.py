from  app.converter import sbol_convert
from  app.converter import gbk_convert

convert_dict = {"sbol" : sbol_convert,
                "gbk" :  gbk_convert}

def file_convert(graph,filename,graph_name,convert_type=None):
    if convert_type is None:
        convert_type = derive_convert_type(filename)
    convert_dict[convert_type.lower()].convert(filename,graph,graph_name)

def get_converter_names():
    return list(convert_dict.keys())
    
def derive_convert_type(filename):
    if filename.lower().endswith(tuple(v.lower() for v in sbol_convert.accepted_file_types)):
        return "sbol"
    if filename.lower().endswith(tuple(v.lower() for v in gbk_convert.accepted_file_types)):
        return "gbk"