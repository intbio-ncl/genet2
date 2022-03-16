import re

from converters.design.utility.util import SBOLGraphUtil
from converters.design.utility.identifiers import identifiers

class SBOLGraph:
    def __init__(self,graph):
        self.graph = SBOLGraphUtil(graph)
    
    def __iter__(self):
        for x in self.graph:
            yield x

    def __len__(self):
        return len(self.graph)

    # ----- RDF-Type searches ------
    def get_all_instances(self):
        return [i[0] for i in self.graph.get_instances()]

    def get_rdf_type(self,subject):
        type_triple = self.graph.get_rdf_type(subject)
        try:
            return type_triple[2]
        except IndexError:
            return None

    def get_component_definitions(self):
        return [cd[0] for cd in self.graph.get_instances(identifiers.objects.component_definition)]

    def get_sequence_annotations(self,cd=None,component=None):
        if cd is not None:
            return [sa[2] for sa in self.graph.get_children(cd,identifiers.predicates.sequence_annotation)]

        sequence_annotations = [cd[0] for cd in self.graph.get_instances(identifiers.objects.sequence_annotation)]
        if component is not None:
            potential_parents = [sa[0] for sa in self.graph.search((None,identifiers.predicates.component,component))]
            sequence_annotations = list(set(sequence_annotations) & set(potential_parents))
        return sequence_annotations


    # ----- Instance searches ----
    def get_definition(self,sub_component):
        try:
            return self.graph.get_definition(sub_component)[2]
        except IndexError:
            return None

    def get_heirachical_instances(self,component_definition):
        components = [fc[0] for fc in self.graph.get_cd_instances(component_definition)
            if self.get_rdf_type(fc[0]) == identifiers.objects.component]
        return components

    def get_functional_instances(self,component_definition):
        functional_components = [fc[0] for fc in self.graph.get_cd_instances(component_definition)
            if self.get_rdf_type(fc[0]) == identifiers.objects.functional_component]
        return functional_components

    # ----- Parent / Child Searches -----
    # - Parent Searches
    def get_parent(self,child):
        for predicate in identifiers.predicates.ownership_predicates:
            try:
                parent = self.graph.get_parent(child,predicate=predicate)[0]
            except (IndexError,TypeError):
                continue
            return parent
        # Component
        parent = self.get_component_definition(component=child)
        if parent is not None:
            return parent
        return None
    
    def get_module_definition(self,fc=None,interaction=None,module=None,maps_to=None):
        parent = []
        if fc is not None:
            parent =  self.graph.get_parent(fc,identifiers.predicates.functional_component)
        elif interaction is not None:
            parent = self.graph.get_parent(interaction,identifiers.predicates.interaction)
        elif module is not None:
            parent = self.graph.get_parent(module,identifiers.predicates.module)
        elif maps_to is not None:
            parent = self.graph.get_parent(maps_to,identifiers.predicates.maps_to)

        try:
            return parent[0]
        except IndexError:
            return None
    
    def get_component_definition(self,component=None,sc=None,sa=None):
        parent =  []
        if component is not None:
            parent = self.graph.get_parent(component,identifiers.predicates.component)
        if sc is not None:
            parent = self.graph.get_parent(sc,identifiers.predicates.sequence_constraint)
        elif sa is not None:
            parent = self.graph.get_parent(sa,identifiers.predicates.sequence_annotation)

        try:
            return parent[0]
        except (IndexError,TypeError):
            return None

    def get_interaction(self,participant):
        try:
            return self.graph.get_parent(participant,identifiers.predicates.participation)[0]
        except IndexError:
            return None

    def get_sequence_annotation(self,location):
        try:
            return self.graph.get_parent(location,identifiers.predicates.location)[0]
        except IndexError:
            return None
    
    def get_combinatorial_derivation(self,variable_component):
        try:
            return self.graph.get_parent(variable_component,identifiers.predicates.variable_component)[0]
        except IndexError:
            return None

    # - Child Searches -
    def get_components(self,component_definition=None):
        components = [sc[2] for sc in self.graph.get_children(component_definition,identifiers.predicates.component)]
        return components

    def get_component(self,sequence_annotation):
        try:
            return self.graph.get_object(sequence_annotation,identifiers.predicates.component,True)[2]
        except IndexError:
            return None

    def get_functional_components(self,module_definition=None):
        components = [sc[2] for sc in self.graph.get_children(module_definition,identifiers.predicates.functional_component)]
        return components

    def get_locations(self,sa=None):
        locations = [sc[2] for sc in self.graph.get_children(sa,identifiers.predicates.location)]
        return locations

    def get_participants(self,fc=None,interaction=None):
        if interaction is not None:
            return [p[2] for p in self.graph.get_children(interaction,identifiers.predicates.participation)]
        if fc is not None:
            return [p[0] for p in self.graph.get_subject(identifiers.predicates.participant,fc)]
        else:
            return [p[2] for p in self.graph.get_children(None,identifiers.predicates.participation)]
    
    def get_participant(self,participation):
        try:
            return self.graph.get_object(participation,identifiers.predicates.participant,True)[2]
        except IndexError:
            return None
    
    def get_sequence_constraints(self,cd=None):
        return [s[2] for s in self.graph.get_children(cd,identifiers.predicates.sequence_constraint)] 

    def get_sequence_names(self,cd):
        sequence_objs = [s[2] for s in self.graph.get_object(cd,identifiers.predicates.sequence)] 
        return sequence_objs
    
    def get_sequences(self,cd=None,sequence_names=None):
        if cd is not None:
            sequence_objs = [s[2] for s in self.graph.get_object(cd,identifiers.predicates.sequence)]
        elif sequence_names is not None:
            if isinstance(sequence_names,list):
                sequence_objs = sequence_names
            else:
                sequence_objs = [sequence_names]
        else:
            sequence_objs = [None]

        sequences = [sequence[2] for sequence_obj in sequence_objs 
                    for sequence in self.graph.get_object(sequence_obj,identifiers.predicates.elements)]
        return sequences

    def get_interactions(self,fc = None):
        if fc is None:
            return [i[0] for i in self.graph.get_instances(identifiers.objects.interaction)]
            
        interactions = []
        participants = self.get_participants(fc)
        for participant in participants:
            interaction = self.get_interaction(participant)
            if interaction is None:
                continue
            interactions.append(interaction)
        return interactions

    # Property Searches
    def get_property(self,subject,predicate):
        try:
            return self.graph.get_object(subject,predicate,single=True)[2]
        except (IndexError,TypeError):
            return None

    def get_properties(self,subject,predicate):
        return [p[2] for p in self.graph.get_object(subject,predicate)]

    def get_type(self,subject):
        try:
            return self.graph.get_type(subject)[2]
        except IndexError:
            return None

    def get_types(self,subject=None,ret_all=False):
        if ret_all:
            return self.graph.get_types(subject)
        else:
            return [t[2] for t in self.graph.get_types(subject)]

    def get_roles(self,subject=None,ret_all=False):
        if ret_all:
            return self.graph.get_roles(subject)
        else:
            return [r[2] for r in self.graph.get_roles(subject)]

    def get_metadata(self,subject):
        m_preds = [identifiers.predicates.role,
                   identifiers.predicates.type]
        return [m[1:] for m in self.search((subject,m_preds,None))]

    def get_triples(self,subject):
        return self.graph.sub_graph((subject,None,None))
    
    def search(self,pattern,lazy=False): 
        return self.graph.search(pattern,lazy)
