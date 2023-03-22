from rdflib import URIRef

from  app.enhancer.data_miner.graph_analyser.utility.util import SBOLGraphUtil
from  app.enhancer.data_miner.graph_analyser.utility.identifiers import identifiers

class SBOLGraph:
    def __init__(self,graph=None):
        self.graph = SBOLGraphUtil(graph)
    
    def __iter__(self):
        for x in self.graph:
            yield x

    def __len__(self):
        return len(self.graph)

    def __iadd__(self, other):
        self.graph += other
        return self    

    # ----- RDF-Type searches ------

    def get_all_instances(self):
        return [i[0] for i in self.graph.get_instances()]

    def get_rdf_type(self,subject):
        if not isinstance(subject,URIRef):
            subject = URIRef(subject)
        type_triple = self.graph.get_rdf_type(subject)
        try:
            return type_triple[2]
        except (IndexError,TypeError):
            return None

    def get_component_definitions(self):
        return [cd[0] for cd in self.graph.get_instances(identifiers.objects.component_definition)]

    def get_sequence_annotations(self,cd=None,component=None,data=False):
        if cd is not None:
            sas = [sa[2] for sa in self.graph.get_children(cd,identifiers.predicates.sequence_annotation)]
        else:
            sas = [cd[0] for cd in self.graph.get_instances(identifiers.objects.sequence_annotation)]
            if component is not None:
                pps = [sa[0] for sa in self.graph.search((None,identifiers.predicates.component,component))]
                sas = list(set(sas) & set(pps))
        
        if not data:
            return sas
        sas_d = []
        for sa in sas:
            triples = self.search((sa,None,None))
            loc = [l[2] for l in triples if l[1] == identifiers.predicates.location]
            assert(len(loc) == 1)
            triples += self.search((loc[0],None,None))
            sas_d.append((sa,triples))
        return sas_d


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
        else:
            return [cd[0] for cd in self.graph.get_instances(identifiers.objects.module_definition)]

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

    def get_component(self,sequence_annotation=None,sequence_constraint=None):
        if sequence_annotation is not None:
            try:
                return self.graph.get_object(sequence_annotation,identifiers.predicates.component,True)[2]
            except TypeError:
                return None

        if sequence_constraint is not None:
            try:
                subj = self.graph.get_object(sequence_constraint,identifiers.predicates.subject,True)[2]
            except IndexError:
                subj = None
            try:
                obj = self.graph.get_object(sequence_constraint,identifiers.predicates.object,True)[2]
            except IndexError:
                subj = None
            return subj,obj
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
            
    def get_modules(self,md):
        return [sc[2] for sc in self.graph.get_children(md,identifiers.predicates.module)]
    
    def get_sequence_constraints(self,cd=None,data=False):
        scs = [s[2] for s in self.graph.get_children(cd,identifiers.predicates.sequence_constraint)]
        if not data:
            return scs
        d_scs = []
        for sc in scs:
            triples = self.search((sc,None,None))
            d_scs.append((sc,triples))
        return d_scs

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

    def get_interactions(self,fc = None,md=None):
        if fc is not None:
            interactions = []
            participants = self.get_participants(fc)
            for participant in participants:
                interaction = self.get_interaction(participant)
                if interaction is None:
                    continue
                interactions.append(interaction)
            return interactions

        if md is not None:
            return [sa[2] for sa in self.graph.get_children(md,identifiers.predicates.interaction)]
        return [i[0] for i in self.graph.get_instances(identifiers.objects.interaction)]
            

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

    def get_type_role(self,subject):
        m_preds = [identifiers.predicates.role,
                   identifiers.predicates.type]
        return [m[1:] for m in self.search((subject,m_preds,None))]

    def get_metadata(self,subject):
        m_preds = [identifiers.predicates.description,
                   identifiers.predicates.mutable_notes,
                   identifiers.predicates.mutable_provenance,
                   identifiers.predicates.title]
        return [m[1:] for m in self.search((subject,m_preds,None))]

    def get_triples(self,subject):
        return self.graph.sub_graph((subject,None,None))
    
    def search(self,pattern,lazy=False): 
        return self.graph.search(pattern,lazy)
