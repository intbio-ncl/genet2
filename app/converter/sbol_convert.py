import re
from rdflib import RDF, BNode, URIRef, DCTERMS, OWL, Literal
from pysbolgraph.SBOL2Serialize import serialize_sboll2
from pysbolgraph.SBOL2Graph import SBOL2Graph
from urllib.parse import urlparse

from app.converter.utility.graph import SBOLGraph
from app.converter.utility.common import map_to_nv, derive_graph_name, get_interaction_properties
from app.graph.utility.model.model import model as model
from app.converter.utility.identifiers import identifiers
from app.utility.change_log.logger import logger
accepted_file_types = ['xml', 'ttl', 'sbol', 'rdf']


'''
1. For each object in data-file (Generally any physical or conceptual entity such as Biological parts or interactions.)
2. Get all properties by mining semantic labels or pre-known keywords.
2. Query internal data-model with properties to find internal objects that match.
3. Add node of object and node of object-type with edge between.
4. Match any properties of object with properties encoded within the data model.
5. If the property links two objects create edge between.
6. Else add node of property and edge between.
'''
nv_seq = model.identifiers.predicates.has_sequence
nv_role = model.identifiers.predicates.role
nv_characteristic = model.identifiers.predicates.hasCharacteristic
nv_physical_entity = model.identifiers.objects.physical_entity
nv_conceptual_entity = model.identifiers.objects.interaction
nv_hasSequence = model.identifiers.predicates.hasSequence
physical_entity = model.identifiers.roles.physical_entity
interaction = model.identifiers.roles.interaction
nv_interaction = model.identifiers.objects.interaction
nv_hasPart = model.identifiers.predicates.hasPart

s_type = identifiers.predicates.type
s_seq = identifiers.predicates.sequence
s_def = identifiers.predicates.definition
s_interaction = identifiers.predicates.interaction
s_functional = identifiers.predicates.functional_component
s_component = identifiers.predicates.component
s_sa = identifiers.predicates.sequence_annotation

s_md = identifiers.objects.module_definition
fc_md = identifiers.objects.functional_component
s_cd = identifiers.objects.component_definition

encoding_dict = {identifiers.objects.DNA: identifiers.objects.naseq,
                 identifiers.objects.DNARegion: identifiers.objects.naseq,
                 identifiers.objects.RNA: identifiers.objects.naseq,
                 identifiers.objects.RNARegion: identifiers.objects.naseq,
                 identifiers.objects.protein: identifiers.objects.amino_acid,
                 identifiers.objects.smallMolecule: identifiers.objects.opensmiles}


def convert(filename, neo_graph, graph_name):
    sbol_graph = SBOLGraph(filename)
    model_roots = model.get_base_class()
    object_type_map = {}
    if graph_name is None or graph_name == "":
        graph_name = derive_graph_name(neo_graph)

    def _add_node(name, type=None, props=None):
        properties = _get_properties(name, sbol_graph, graph_name)
        if props is not None:
            properties.update(props)
        neo = neo_graph.add_node(name, type, **properties)
        return neo

    def _add_edge(n, v, e):
        properties = _get_properties(e, sbol_graph, graph_name)
        neo_graph.add_edge(n, v, str(e), **properties)

    for cd in sbol_graph.get_component_definitions():
        properties = ([(nv_characteristic, physical_entity)] +
                      [(nv_role, r) for r in (sbol_graph.get_roles(cd)+sbol_graph.get_types(cd))])

        s, p, o = map_to_nv(cd, properties, model_roots, model)
        sequence = sbol_graph.get_sequences(cd)
        if len(sequence) > 0:
            assert(len(sequence) == 1)
            props = {model.identifiers.predicates.hasSequence: sequence[0]}
        else:
            props = None
        n = _add_node(s, o, props)
        object_type_map[s] = o
        for p, o in _map_entities(cd, sbol_graph, model):
            o = _add_node(o)
            _add_edge(n, o, p)

    for i in sbol_graph.get_interactions():
        roles = ([(nv_characteristic, interaction)] +
                 [(nv_role, r) for r in (sbol_graph.get_types(i))])
        s, p, o = map_to_nv(i, roles, model_roots, model)
        n = _add_node(s, o)
        for s, p, o in get_interaction_properties(i, o, object_type_map, model, sbol_graph):
            if p == RDF.type:
                s = _add_node(s, o)
            else:
                s = _add_node(s)
                o = _add_node(o)
                _add_edge(s, o, p)
    neo_graph.submit(log=False)


def export(fn, gn):
    c_dict = {"add": {"node": _add_node,
                      "edge": _add_edge},
              "remove": {"node": _remove_node,
                         "edge": _remove_edge},
              "replace": {"node": _replace_node,
                          "edge" : _replace_edge}}
    try:
        changes = logger.get_changes(gn)
    except ValueError:
        # When no changes have been made.
        return fn

    g = SBOLGraph(fn)
    for change in changes:
        g = c_dict[change["action"]][change["type"]](change, g)
    g = _handle_deferals(g)
    pysbolG = SBOL2Graph()
    pysbolG += g
    sbol = serialize_sboll2(pysbolG).decode("utf-8")

    with open(fn, 'w') as o:
        o.write(sbol)    
    logger.remove_graph(gn)
    return fn


def _add_node(change, graph):
    node = change["subject"]
    nt = node.get_type()
    if nt == "None":
        return graph
    if model.is_derived(URIRef(nt), nv_physical_entity):
        o_type, o_role = _derive_type_role(node.get_type())
        if o_type is None:
            o_type, o_role = o_role,o_type
        properties = _cast_properties(node.get_properties())
        if nv_hasSequence in properties:
            sn = graph.create_sequence_name(node.get_key())
            graph.add_sequence(sn,properties[nv_hasSequence],identifiers.objects.naseq)
            del properties[nv_hasSequence]
        else:
            sn = None
        graph.add_component_definition(node.get_key(), o_type, o_role, sequence=sn,properties=properties)
    elif model.is_derived(URIRef(node.get_type()), nv_conceptual_entity):
        # Need to derive its parent.
        # A deferal its potential participants and parent are known.
        _,o_role =  _derive_type_role(node.get_type())
        properties = _cast_properties(node.get_properties())
        graph.add_interaction(node.get_key(), o_role, **properties)
    else:
        print(f'{node} cant be added to SBOL Graph')
    return graph

def _add_edge(change, graph):
    edge = change["subject"]
    e_type = URIRef(edge.get_type())
    if e_type == nv_hasPart:
        # Could we add SC or SA in here?
        n = URIRef(edge.n.get_key())
        v = URIRef(edge.v.get_key())
        cn = graph.build_children_uri(n,v)
        graph.add_component(cn,v,n)
    elif e_type in [p[1]["key"] for p in model.interaction_predicates()]:
        if not model.is_derived(edge.n.get_type(),nv_interaction):
            raise ValueError(f'Outgoing edge {edge} is not a Interaction')
        if not model.is_derived(edge.v.get_type(),nv_physical_entity):
            raise ValueError(f'Incoming edge {edge} is not a Physical Entity')
        n = URIRef(edge.n.get_key())
        v = URIRef(edge.v.get_key())
        role = _derive_edge_role(edge.get_type())
        pn = graph.create_part_name(n,v,role)
        fc = _derive_fc(n,v,graph)
        graph.add_participation(pn,fc,role,n)
    else:
        print(f'{e_type} Cant be added to SBOL Graph')
    return graph

def _remove_node(change, graph):
    subj = URIRef(change["subject"])
    subj_type = graph.get_rdf_type(subj)
    if subj_type == identifiers.objects.component_definition:
        graph.remove_component_definition(subj)
    elif subj_type == identifiers.objects.interaction:
        graph.remove_interaction(subj)
    return graph

def _remove_edge(change, graph):
    edge = change["subject"]
    e_type = URIRef(edge.get_type())
    if e_type == nv_hasPart:
        n = URIRef(edge.n.get_key())
        v = URIRef(edge.v.get_key())
        for c in graph.get_components(n):
            if graph.get_definition(c) == v:
                graph.remove_component(c)
    elif e_type in [p[1]["key"] for p in model.interaction_predicates()]:
        n = URIRef(edge.n.get_key())
        v = URIRef(edge.v.get_key())
        for p in graph.get_participants(interaction=n):
            fc = graph.get_participant(p)
            fc_t = graph.get_rdf_type(fc)
            if fc_t == identifiers.objects.component_definition:
                fc_d = fc
            else:
                fc_d = graph.get_definition(fc)
            if URIRef(fc_d) == v:
                graph.remove_participants(p)
    else:
        raise NotImplementedError(f'{e_type}')
    return graph

def _replace_node(change, graph):
    subj = URIRef(change["subject"])
    pred = change["predicate"]
    obj = change["object"]
    if pred == "uri":
        graph.replace_uri(subj,URIRef(obj))
    elif URIRef(pred) == nv_hasSequence:
        graph.replace_sequence(subj,Literal(obj))
    elif URIRef(pred) == DCTERMS.description:
        graph.replace_property(subj,URIRef(pred),Literal(obj))
    return graph

def _replace_edge(change,graph):
    subj = change["subject"]
    pred = change["predicate"]
    obj = change["object"]
    if pred == "uri":
        graph.replace_uri(subj,URIRef(obj))
    elif URIRef(pred) == nv_hasSequence:
        graph.replace_sequence(subj,Literal(obj))
    elif URIRef(pred) == DCTERMS.description:
        graph.replace_property(subj,URIRef(pred),Literal(obj))
    return graph

def _handle_deferals(graph):
    # Deferals namely refer to cases where parents of interactions 
    # cant be identified OR the parents of participants to interactions can be found.
    # The first step if find BNOdes and then swap with fcs
    # Secondly derived MD parents for Interactions based on parts -> FC parents.
    for s,p,o in graph.get_participants():
        if isinstance(o,BNode):
            cd_fc = graph.get_functional_instances(URIRef(o))
            inter = graph.get_interaction(s)
            i_ps = [pa for pa in graph.get_participants(interaction=inter) if pa != s]
            i_ps_fc = [graph.get_participant(p) for p in i_ps]
            i_ps_fc_pas = [graph.get_module_definition(fc=fc) for fc in i_ps_fc]
            i_ps_fc_pas = [md for md in i_ps_fc_pas if md is not None]
            cd_fc_mds = [graph.get_module_definition(fc=fc) for fc in cd_fc]
            if len(i_ps_fc_pas) > 0:
                assert(len(i_ps_fc_pas) == 1)
                for fc in cd_fc:
                    fc_md = graph.get_module_definition(fc=fc)
                    if fc_md in i_ps_fc_pas:
                        graph.replace_triple((s,p,o),(s,p,fc))
                        break
                else:
                    # NEW FC IN Parent of other part.
                    fc_name = graph.create_fc_name(inter,o)
                    graph.add_functional_component(fc_name,o,parent=i_ps_fc_pas[0])
                    graph.replace_triple((s,p,o),(s,p,fc_name))
            elif len(cd_fc_mds) > 0:
                graph.replace_triple((s,p,o),(s,p,cd_fc[0]))
            else:
                o_uri = URIRef(o)
                md_name = graph.create_md_name(o_uri)
                graph.add_module_definition(md_name)
                fc_name = graph.create_fc_name(md_name,o_uri)
                graph.add_functional_component(fc_name,o_uri,md_name)
                graph.replace_triple((s,p,o),(s,p,fc_name))
    for interaction in graph.get_interactions():
        parts = graph.get_participants(interaction=interaction)
        fcs = [graph.get_participant(p) for p in parts]
        mds = list(set([graph.get_module_definition(fc=fc) for fc in fcs]))
        assert(len(mds) == 1)
        graph.add_triple((mds[0],identifiers.predicates.interaction,interaction))
    return graph

def _cast_properties(properties):
    c_props = {}
    for k,v in properties.items():
        if urlparse(k).netloc == "":
            continue
        if urlparse(v).netloc != "":
            v = URIRef(v)
        else:
            v = Literal(v)
        c_props[URIRef(k)] = v
    return c_props

def _derive_fc(interaction,cd,graph):
    parent = graph.get_module_definition(interaction=interaction)
    cd_fc = graph.get_functional_instances(cd)
    int_parts = graph.get_participants(interaction=interaction)
    int_parts_fc = [graph.get_participant(p) for p in int_parts]
    int_parts_fc_parents = [graph.get_module_definition(fc=fc) for fc in int_parts_fc]
    int_parts_fc_parents = [md for md in int_parts_fc_parents if md is not None]
    if parent is not None:
        md_fcs = graph.get_functional_components(parent)
        inter = list(set(md_fcs) & set(cd_fc))
        # CD has FC in parent
        if len(inter) > 0:
            return inter[0]
        else:
            fc_name = graph.create_fc_name(interaction,cd)
            graph.add_functional_component(fc_name,cd)
            return fc_name
    # Other Parts exist.
    if len(int_parts_fc_parents) > 0:
        # Are any fcs a children of a part fc
        for fc in cd_fc:
            fc_md = graph.get_module_definition(fc=fc)
            if fc_md in int_parts_fc_parents:
                return fc
        else:
            # NEW FC IN Parent of other part.
            fc_name = graph.create_fc_name(interaction,cd)
            graph.add_functional_component(fc_name,cd)
            return fc_name
    else:
        return BNode(cd)

def _derive_type_role(o_type):
    otcc = model.get_class_code(o_type)
    otype = None
    role = None
    for p,v in model.get_equivalent_classes(otcc)[0][0][1]:
        if p == RDF.type:
            if v[1]["key"] != nv_physical_entity and v[1]["key"] != nv_interaction:
                _,otype = _derive_type_role(v[1]["key"])
        if p == OWL.unionOf:
            pred,val = v[0]
            if pred == nv_role:
                role = val[0][1]["key"]
    return otype,role

def _derive_edge_role(o_type):
    otcc = model.get_class_code(o_type)
    return model.get_equivalent_properties(otcc)[0][1]["key"]

def _map_entities(cd, sbol_graph, model):
    triples = []
    part_of = model.identifiers.predicates.hasPart
    for sc in [sbol_graph.get_definition(c) for c in sbol_graph.get_components(cd)]:
        triples.append((part_of, sc))
    return triples

def _get_properties(entity, graph, graph_name):
    properties = {}
    if isinstance(entity, URIRef):
        properties["dtype"] = "URI"
    elif isinstance(entity, BNode):
        properties["dtype"] = "BNode"
    else:
        properties["dtype"] = "Literal"
    meta = graph.get_metadata(entity)
    properties["name"] = _get_name(entity)
    properties["graph_name"] = [graph_name]
    if len(meta) > 0:
        properties[DCTERMS.description] = meta
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
