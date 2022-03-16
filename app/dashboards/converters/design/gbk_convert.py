from Bio import SeqIO
import networkx as nx
from rdflib import RDF,URIRef
from converters.utility import get_name,map_to_nv

accepted_file_types = ['gbk','gb']
blacklist_features = ["source","exon"]
potential_type_quals = ["regulatory_class","note"]
potential_name_quals = ["note","gene","label"]

def convert(input_fn,model_graph):
    graph = nx.MultiDiGraph()
    ids = model_graph.identifiers
    node_count = 1
    node_map = {}
    subject_list = []
    model_roots = model_graph.get_base_class()
    nv_role = ids.predicates.role
    nv_characteristic = model_graph.identifiers.predicates.hasCharacteristic
    physical_entity = model_graph.identifiers.roles.physical_entity
    part_of = model_graph.identifiers.predicates.hasPart
    text_map = gbk_map(ids)

    def _add_node(entity,node_count):
        if entity in node_map.keys():
            n_key = node_map[entity]
        else:
            n_key = node_count
            node_map[entity] = n_key
            node_count += 1
        if isinstance(entity, URIRef):
            e_type = "URI"
        else:
            e_type = "Literal"
        graph.add_node(n_key, key=entity,type=e_type)
        return n_key,node_count
        
    for record in SeqIO.parse(open(input_fn,"r"), "genbank"):
        name = record.name
        if record.name is None and record.name == "":
            name = record.id
        subject = ids.namespaces.nv + name
        properties = [(nv_characteristic,physical_entity),(nv_role,ids.roles.dna)]
        s,p,o = map_to_nv(subject,properties,model_roots,model_graph)
        n,node_count = _add_node(s,node_count)
        v,node_count = _add_node(o,node_count)
        name = get_name(p)
        graph.add_edge(n,v,key=p,display_name=name,weight=1)
        features = {}
        for f in record.features:
            if f.type in blacklist_features:
                continue
            if str(f.location) in features:
                features[str(f.location)].append(f)
            else:
                features[str(f.location)] = [f]

        for k,feature in features.items():
            f_types = [f.type for f in feature]
            quals = {}
            for f in feature:
                quals.update(f.qualifiers)
            if any(x in f_types for x in blacklist_features):
                continue
            names = []
            types = f_types

            for k,v in quals.items():
                if k in potential_name_quals:
                    if isinstance(v,list):
                        names += [a.replace(" ","-") for a in v]
                    else:
                        names.append(v.replace(" ","-"))
                if k in potential_type_quals:
                    if isinstance(v,list):
                        types += v
                    else:
                        types.append(v)

            f_subject = URIRef(subject + "/" + names[0])
            count = 1
            while True:
                if f_subject not in subject_list:
                    break
                for name in names:
                    f_subject = URIRef(subject + "/" + name)
                    if f_subject not in subject_list:
                        break
                else:
                    f_subject = URIRef(subject + "/" + names[0] + "_" + str(count))
                count += 1

            subject_list.append(f_subject)
            for t in types:
                try:
                    obj = text_map[t.upper()]
                    break
                except KeyError:
                    continue
            else:
                obj = ids.roles.dna

            p = properties + [(nv_role,obj)]
            f_s,f_p,f_o = map_to_nv(f_subject,p,model_roots,model_graph)
            f_n,node_count = _add_node(f_s,node_count)
            f_v,node_count = _add_node(f_o,node_count)
            name = get_name(f_p)
            dp = get_name(part_of)
            graph.add_edge(f_n,f_v,key=f_p,display_name=name,weight=1)
            graph.add_edge(n,f_n,key=part_of,dislay_name=dp,weight=1)
    return graph

def gbk_map(ids):
    return {
    "DNA": ids.roles.dna,
    "PROMOTER":ids.roles.promoter,
    "RBS":ids.roles.rbs,
    "CDS":ids.roles.cds,
    "TERMINATOR":ids.roles.terminator
}