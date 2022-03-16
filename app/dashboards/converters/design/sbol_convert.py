import re
import networkx as nx
from rdflib import RDF,BNode,URIRef
from converters.design.utility.graph import SBOLGraph
from converters.utility import map_to_nv, get_name

accepted_file_types = ['xml','ttl','sbol','rdf']
def convert(filename,model_graph):
    graph = nx.MultiDiGraph()
    sbol_graph = SBOLGraph(filename)
    model_roots = model_graph.get_base_class()
    node_count = 1
    node_map = {}

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

    nv_role = model_graph.identifiers.predicates.role
    nv_characteristic = model_graph.identifiers.predicates.hasCharacteristic
    physical_entity = model_graph.identifiers.roles.physical_entity
    for cd in sbol_graph.get_component_definitions():
        properties = ([(nv_characteristic,physical_entity)] + 
                     [(nv_role,r) for r in (sbol_graph.get_roles(cd)+sbol_graph.get_types(cd))])

        s,p,o = map_to_nv(cd,properties,model_roots,model_graph)
        n,node_count = _add_node(s,node_count)
        v,node_count = _add_node(o,node_count)
        name = get_name(p)
        graph.add_edge(n,v,key=p,display_name=name,weight=1)

        for p,o in _map_entities(cd,sbol_graph,model_graph):
            dp = get_name(p)
            o,node_count = _add_node(o,node_count)
            graph.add_edge(n,o,key=p,dislay_name=dp,weight=1)

    for i in sbol_graph.get_interactions():
        conceptual_entity = model_graph.identifiers.roles.interaction
        roles = ([(nv_characteristic,conceptual_entity)] + 
                [(nv_role,r) for r in (sbol_graph.get_types(i))])
        s,p,o = map_to_nv(i,roles,model_roots,model_graph)
        n,node_count = _add_node(s,node_count)
        v,node_count = _add_node(o,node_count)
        name = get_name(p)
        graph.add_edge(n,v,key=p,display_name=name,weight=1)
        for s,p,o in _get_interaction_properties(i,o,graph,model_graph,sbol_graph):
            s,node_count = _add_node(s,node_count)
            o,node_count = _add_node(o,node_count)
            p_name = get_name(p)
            graph.add_edge(s,o,key=p,display_name=p_name,weight=1)
    return graph

def _get_interaction_properties(identity,i_type,i_graph,m_graph,s_graph):
    triples = []
    subject_list = []
    i_type_c = m_graph.get_class_code(i_type)
    prop = m_graph.get_class_properties(i_type_c)
    io_data = _get_io_data(identity,i_graph,m_graph,s_graph)
    restrictions = _get_restrictions(i_type_c,m_graph)
    for p,p_data in prop:
        p_key = p_data["key"]
        # Ontology - Property references data in NV.
        if p_key in restrictions.keys():
            restriction = restrictions[p_key]
            cur_node = BNode()
            triples.append((identity,p_key,cur_node))
            for index,(pred,element) in enumerate(restriction):
                e,e_data = element
                e_key = e_data["key"]
                e_id,e_triples = _build_restriction_obj(identity,pred,e_key,subject_list)
                subject_list.append(e_id)
                if index == len(restriction) -1:
                    next_node = RDF.nil
                else:
                    next_node = BNode()
                triples.append((cur_node,RDF.first,e_id))
                triples.append((cur_node,RDF.rest,next_node))
                triples += e_triples
                cur_node = next_node

        # SBOL Graph - Property references data in design.
        else:
            # Check participant is of correct NV:type
            r_id,r_data = m_graph.get_range(p)
            potential_ios = []
            for r,data in m_graph.get_union(r_id):
                for r in m_graph.resolve_union(r):
                    pred,val = r
                    for io in io_data:
                        child = io[pred]
                        parent = val[1]["key"]
                        if (pred in io.keys() and 
                           (child == parent or m_graph.is_derived(child,val[0]))):
                            potential_ios.append(io)
            equivalents = m_graph.get_equivalent_properties(p)
            for io in potential_ios:
                metadata = io["meta"]
                for e_id,e_data in equivalents:
                    if e_data["key"] in metadata:
                        triples.append((identity,p_key,io["definition"]))
                        break
    return triples


def _build_restriction_obj(parent,predicate,value,curr_subjects):
    if parent[-1].isdigit:
        parent = parent[:-1]
    name = URIRef(parent + get_name(value))
    count = 1
    while name in curr_subjects:
        name = URIRef(f'{name}/{count}')
        count += 1
    triples = [(name,predicate,value)]
    return name,triples

def _get_io_data(identity,i_graph,m_graph,s_graph):
    # Gets metadata and RDF type for each SBOL: participant (i/o elements).
    object_data = []
    for p in s_graph.get_participants(interaction=identity):
        definition = s_graph.get_definition(s_graph.get_participant(p))
        object_data.append({"definition" : definition,
                            "meta" : [m[-1] for m in s_graph.get_metadata(p)],
                            RDF.type : _get_nv_type(definition,i_graph,m_graph)})
    return object_data

def _get_restrictions(i_type_c,m_graph):
    # Get restrictions from ontology for a given interaction.
    restrictions = {}
    for restriction in m_graph.get_restrictions_on(i_type_c):
        predicate,constraints = m_graph.get_constraint(restriction)
        restrictions[predicate] = constraints
    return restrictions

def _map_entities(cd,sbol_graph,model_graph):
    triples = []
    part_of = model_graph.identifiers.predicates.hasPart
    for sc in [sbol_graph.get_definition(c) for c in sbol_graph.get_components(cd)]:
        triples.append((part_of,sc))
    return triples

def _get_nv_type(key,graph,m_graph):
    for n,v,k in graph.edges(keys=True):
        n_data = graph.nodes[n]
        v_data = graph.nodes[v]
        if n_data["key"] == key and k == RDF.type:
            return v_data["key"]
    return m_graph.identifiers.roles.physical_entity

