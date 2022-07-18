import re
from Bio import SeqIO
from rdflib.namespace import DC
from rdflib import BNode,RDF,URIRef
from  app.graph.design_graph.converter.common import map_to_nv, get_name
from  app.graph.utility.model.model import model as model_graph

accepted_file_types = ['gbk', 'gb']
blacklist_features = ["source", "exon"]
potential_type_quals = ["regulatory_class","note"]
potential_name_quals = ["note","gene","label"]

def convert(input_fn,graph,mode,graph_name):
    ids = model_graph.identifiers
    subject_list = []
    model_roots = model_graph.get_base_class()
    nv_role = ids.predicates.role
    nv_characteristic = ids.predicates.hasCharacteristic
    physical_entity = ids.roles.physical_entity
    interaction = ids.roles.interaction
    gp = ids.roles.genetic_production
    part_of = ids.predicates.hasPart
    has_seq = ids.predicates.hasSequence
    text_map = gbk_map(ids)

    def _add_node(name, type=None,properties = {}):
        properties.update(_get_properties(name, graph_name))
        return graph.add_node(name, type, mode=mode, **properties)

    def _add_edge(n, v, e):
        properties = _get_properties(e, graph_name)
        return graph.add_edge(n, v, str(e), mode=mode, **properties)

    def _new_name(names):
        f_subject = subject + "/" + names[0]
        count = 1
        while True:
            if f_subject not in subject_list:
                break
            for name in names:
                f_subject = subject + "/" + name
                if f_subject not in subject_list:
                    break
            else:
                f_subject = subject + "/" + names[0] + "_" + str(count)
            count += 1
        subject_list.append(f_subject)
        return f_subject

    fh = open(input_fn,"r")

    for record in SeqIO.parse(fh, "genbank"):
        name = record.name
        seq = record.seq
        if record.name is None and record.name == "":
            name = record.id
        subject = ids.namespaces.nv + name
        sources = [f for f in record.features if f.type == "source"]
        props = []
        for source in sources:
            for k,v in source.qualifiers.items():
                    if isinstance(v,list):
                        props += v
                    else:
                        props.append(v) 
        s_props = {DC.description : props}
        properties = [(nv_characteristic,physical_entity),(nv_role,ids.roles.dna)]
        s,p,o = map_to_nv(subject,properties,model_roots,model_graph)
        n = _add_node(s,o,s_props)
        features = {}
        for f in record.features:
            if f.type in blacklist_features:
                continue
            if (f.location.start,f.location.end) in features:
                features[(f.location.start,f.location.end)].append(f)
            else:
                features[(f.location.start,f.location.end)] = [f]

        for location,feature in features.items():
            f_types = [f.type for f in feature]
            quals = {}
            for f in feature:
                quals.update(f.qualifiers)
            if any(x in f_types for x in blacklist_features):
                continue
            names = []
            props = []
            ints = []
            types = f_types
            for k,v in quals.items():
                if k in potential_name_quals:
                    if isinstance(v,list):
                        names += [a.replace(" ","-") for a in v]
                        props += v
                    else:
                        names.append(v.replace(" ","-"))
                        props.append(v)
                if k in potential_type_quals:
                    if isinstance(v,list):
                        types += v
                        props += v
                    else:
                        types.append(v)
                        props.append(v)
                if k == "product":
                    if isinstance(v,list):
                        ints += v
                    else:
                        ints.append(v)
            f_subject = _new_name(names)
            for t in types:
                try:
                    obj = text_map[t.upper()]
                    break
                except KeyError:
                    continue
            else:
                obj = ids.roles.dna
            
            p = properties + [(nv_role,obj)]
            f_s,_,f_o = map_to_nv(f_subject,p,model_roots,model_graph)
            s_seq = seq[location[0]:location[1]]            
            props = {DC.description : props,
                     has_seq : s_seq}
            f_n = _add_node(f_s,f_o,props)
            _add_edge(n,f_n,part_of)
            
            for int_obj in ints:
                roles = [(nv_characteristic, interaction),(nv_role, gp)]
                if int_obj == _get_name(f_subject):
                    prot = f'{int_obj}_p'
                else:
                    prot = int_obj
                i = f'{int_obj}_protein_production'
                i = _new_name([i])
                prot = _new_name([prot])
                int_obj, _, int_type = map_to_nv(i, roles, model_roots, model_graph)
                int_obj = _add_node(int_obj,int_type)
                prot = _add_node(prot,ids.objects.protein)
                _add_edge(int_obj, prot, ids.predicates.product)
                _add_edge(int_obj, f_subject, ids.predicates.template)
                for s1, p1, o1 in _get_interaction_properties(i, int_type, model_graph):
                    if p1 == RDF.type:
                        s1 = _add_node(s1,o1)
                    else:
                        s1 = _add_node(s1)
                        o1 = _add_node(o1)
                        _add_edge(s1, o1, p1)
        

    fh.close()
    graph.submit()
    return graph

def gbk_map(ids):
    return {
        "DNA": ids.roles.dna,
        "PROMOTER": ids.roles.promoter,
        "RBS": ids.roles.rbs,
        "CDS": ids.roles.cds,
        "TERMINATOR": ids.roles.terminator
    }

def _get_interaction_properties(identity, i_type, m_graph):
    triples = []
    subject_list = []
    i_type_c = m_graph.get_class_code(i_type)
    prop = m_graph.get_class_properties(i_type_c)
    restrictions = _get_restrictions(i_type_c, m_graph)
    ip = m_graph.interaction_predicates()
    for p, p_data in prop:
        p_key = p_data["key"]
        # Ontology - Property references data in NV.
        if p_key in restrictions.keys():
            restriction = restrictions[p_key]
            cur_node = BNode(identity + "/" + get_name(p_key) + "/0")
            triples.append((identity, p_key, cur_node))
            for index, (pred, element) in enumerate(restriction):
                e, e_data = element
                e_key = e_data["key"]
                e_id, e_triples = _build_restriction_obj(
                    identity, pred, e_key, subject_list)
                subject_list.append(e_id)
                if index == len(restriction) - 1:
                    next_node = RDF.nil
                else:
                    next_node = BNode(
                        identity + "/" + get_name(p_key) + "/" + str(index+1))
                triples.append((cur_node, RDF.first, e_id))
                triples.append((cur_node, RDF.rest, next_node))
                triples += e_triples
                cur_node = next_node
    return triples

def _get_restrictions(i_type_c, m_graph):
    # Get restrictions from ontology for a given interaction.
    restrictions = {}
    for restriction in m_graph.get_restrictions_on(i_type_c):
        predicate, constraints = m_graph.get_constraint(restriction)
        restrictions[predicate] = constraints
    return restrictions

def _build_restriction_obj(parent, predicate, value, curr_subjects):
    if parent[-1].isdigit:
        parent = parent[:-1]
    name = URIRef(parent + get_name(value))
    count = 1
    while name in curr_subjects:
        name = URIRef(f'{name}/{count}')
        count += 1
    triples = [(name, predicate, value)]
    return name, triples

def _get_properties(uri, graph_name):
    properties = {}
    properties["name"] = _get_name(uri)
    properties["graph_name"] = [graph_name]
    return properties

def _get_name(subject):
    split_subject = _split(subject)
    if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
        return split_subject[-2]
    elif len(split_subject[-1]) == 3 and _isfloat(split_subject[-1]):
        return split_subject[-2]
    else:
        return split_subject[-1]


def _split(uri):
    return re.split('#|\/|:', uri)


def _isfloat(x):
    try:
        float(x)
        return True
    except ValueError:
        return False
