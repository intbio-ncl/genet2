from rdflib import RDF,OWL,BNode,URIRef
import re

def map_to_nv(identifier,properties,roots,model):
    def model_requirement_depth(nv_class,parent_class=None,depth=0):
        def is_equivalent_class(class_id):
            ecs = model.get_equivalent_classes(class_id)
            if len(ecs) == 0:
                # Classes with no equivalents
                # For us that is just the base class.
                return True
            return _meets_requirements(ecs,parent_class,properties)

        class_id,c_data = nv_class
        if not is_equivalent_class(class_id):
            return (depth,parent_class)
        depth +=1
        # All Requirements met.
        children = model.get_child_classes(class_id)
        cur_lowest_child = (depth,nv_class)
        for child in children:
            ret_val = model_requirement_depth(child,nv_class,depth)
            if ret_val[0] > cur_lowest_child[0]:
                cur_lowest_child = ret_val
        # Get most specialised children or self
        return cur_lowest_child

    for root in roots:
        possible_class = model_requirement_depth(root)
        return (identifier,RDF.type,possible_class[1][1]["key"])

def get_interaction_properties(identity, i_type, object_type_map, m_graph, s_graph,add_nv_props=True):
    triples = []
    subject_list = []
    i_type_c = m_graph.get_class_code(i_type)
    prop = m_graph.get_class_properties(i_type_c)
    io_data = _get_io_data(identity, object_type_map, m_graph, s_graph)
    restrictions = _get_restrictions(i_type_c, m_graph)

    for p, p_data in prop:
        p_key = p_data["key"]
        # Ontology - Property references data in NV.
        if p_key in restrictions.keys():
            if not add_nv_props:
                continue
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

        # SBOL Graph - Property references data in design.
        else:
            # Check participant is of correct NV:type
            r_id, r_data = m_graph.get_range(p)
            potential_ios = []
            for r, data in m_graph.get_union(r_id):
                for r in m_graph.resolve_union(r):
                    pred, val = r
                    for io in io_data:
                        child = URIRef(io[pred])
                        parent = val[1]["key"]
                        if (pred in io.keys() and
                           (child == parent or m_graph.is_derived(child, val[0]))):
                            potential_ios.append(io)
            equivalents = m_graph.get_equivalent_properties(p)
            for io in potential_ios:
                metadata = io["meta"]
                for e_id, e_data in equivalents:
                    if e_data["key"] in metadata:
                        triples.append((identity, p_key, io["definition"]))
                        break
    return triples

def _get_io_data(identity, object_type_map, m_graph, s_graph):
    # Gets metadata and RDF type for each SBOL: participant (i/o elements).
    object_data = []
    for p in s_graph.get_participants(interaction=identity):
        definition = s_graph.get_definition(s_graph.get_participant(p))
        object_data.append({"definition": definition,
                            "meta": [m[-1] for m in s_graph.get_type_role(p)],
                            RDF.type: _get_nv_type(definition, object_type_map)})
    return object_data

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

def _get_nv_type(key, object_type_map):
    return object_type_map[key]

def _get_restrictions(i_type_c, m_graph):
    # Get restrictions from ontology for a given interaction.
    restrictions = {}
    for restriction in m_graph.get_restrictions_on(i_type_c):
        predicate, constraints = m_graph.get_constraint(restriction)
        restrictions[predicate] = constraints
    return restrictions

def _meets_requirements(equiv_classes,parent_class,properties):
    def _meets_requirements_inner(equiv_type,requirements,parent_class):
        if equiv_type == OWL.intersectionOf:
            # Equivalent Class with extras.
            # All extras must be met.
            for r in requirements:
                if not _meets_requirements_inner(*r,parent_class):
                    return False
        elif equiv_type == OWL.unionOf:
            # Equiv Class with optional extras.
            for r in requirements:
                if _meets_requirements_inner(*r,parent_class):
                    return True
            else:
                return False
        elif equiv_type == RDF.type:
            # Direct Equivalent Class.
            if requirements[1] == RDF.type and requirements[0]["key"] != parent_class[1]["key"]:
                return False
        else:
            # Single properties (Not Class)
            value,constraint = requirements
            value = value[1]["key"]
            if constraint == OWL.hasValue and (equiv_type,value) not in properties:
                return False
            elif constraint == OWL.cardinality:
                for t,v in properties:
                    if v is None:
                        v = []
                    if t == equiv_type and len(v) == int(value):
                        break
                else:
                    return False
            elif constraint == OWL.minCardinality:
                for t,v in properties:
                    if v is None:
                        v = []
                    if t == equiv_type and len(v) >= int(value):
                        break
                else:
                    return False
            elif constraint == OWL.maxCardinality:
                for t,v in properties:
                    if v is None:
                        v = []
                    if t == equiv_type and len(v) <= int(value):
                        break
                else:
                    return False

        return True
        
    for equiv_class in equiv_classes:
        # Each Requirement must be met.
        for equiv_type,requirements in equiv_class:
            if not _meets_requirements_inner(equiv_type,requirements,parent_class):
                break
        else:
            return True
    else:
        return False

def derive_graph_name(graph):
    graph_names = graph.get_graph_names()
    graph_name = 1
    while str(graph_name) in graph_names:
        graph_name += 1
    return str(graph_name)

def get_name(subject):
    split_subject = _split(subject)
    if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
        return split_subject[-2]
    else:
        return split_subject[-1]

def _split(uri):
    return re.split('#|\/|:', uri)