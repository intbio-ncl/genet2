from rdflib import RDF,OWL
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

def _derive_graph_name(graph):
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