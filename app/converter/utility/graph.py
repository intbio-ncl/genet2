from rdflib import URIRef,RDF,Literal,BNode
import re
from  app.converter.utility.util import SBOLGraphUtil
from  app.converter.utility.identifiers import identifiers

class SBOLGraph:
    def __init__(self,graph=None):
        self.graph = SBOLGraphUtil(graph)
    
    def __iter__(self):
        for x in self.graph:
            yield x

    def __len__(self):
        return len(self.graph)

    def __add__(self,obj):
        return self.__class__(self.graph.graph + obj.graph.graph)

    def __sub__(self,obj):
        return self.__class__(self.graph.graph - obj.graph.graph)


    # ----- RDF-Type searches ------
    def add_triple(self,triple):
        self._add_triples([triple])
        
    def remove_triple(self,triple):
        self._remove_triples([triple])

    def replace_uri(self,old,new):
        for s,p,o in self.search((old,None,None)):
            self._remove_triples([(s,p,o)])
            self._add_triples([(new,p,o)])
        for s,p,o in self.search((None,None,old)):
            self._remove_triples([(s,p,o)])
            self._add_triples([(s,p,new)])
        old = BNode(old)
        for s,p,o in self.search((None,None,old)):
            self._remove_triples([(s,p,o)])
            self._add_triples([(s,p,BNode(new))])

    def replace_sequence(self,subject,seq):
        seqs = self.get_sequence_names(subject)[0]
        if len(self.search((None,identifiers.predicates.sequence,seqs))) == 1:
            self._remove_triples([(seqs,identifiers.predicates.elements,None)])
            self._add_triples([(seqs,identifiers.predicates.elements,seq)])
        else:
            sn = self.create_sequence_name(subject)
            self.add_sequence(sn,Literal(seq),identifiers.objects.naseq)
            self._remove_triples([(subject,identifiers.predicates.sequence,seqs)])

    def replace_property(self,subject,predicate,property):
        self._remove_triples(self.search((subject,predicate,None)))
        self._add_triples([(subject,predicate,property)])

    def replace_triple(self,old,new):
        self._remove_triples([old])
        self._add_triples([new])


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
        except (IndexError,TypeError):
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
        except (IndexError,TypeError):
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
            return self.graph.get_children(None,identifiers.predicates.participant)
    
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
        md = []
        for m in self.search((subject,m_preds,None)):
            md.append(m[2].replace('"',""))
        return md
        
    def get_triples(self,subject):
        return self.graph.sub_graph((subject,None,None))
    
    def search(self,pattern,lazy=False): 
        return self.graph.search(pattern,lazy)

    def _add_triples(self,triples):
        self.graph.add_triples(triples)

    def _remove_triples(self,triples):
        self.graph.remove_triples(triples)

    def _generic_generation(self,uri,type):
        if not isinstance(uri,URIRef):
            uri = URIRef(uri)
        triples = [(uri,RDF.type,type)]
        triples.append((uri,identifiers.predicates.persistent_identity,_get_pid(uri)))
        triples.append((uri,identifiers.predicates.display_id,Literal(_get_name(uri))))
        triples.append((uri,identifiers.predicates.version,Literal(1)))
        return triples

    def add_sequence(self,uri,sequence,encoding):
        triples = self._generic_generation(uri,identifiers.objects.sequence)
        triples.append((uri,identifiers.predicates.elements,sequence))
        triples.append((uri,identifiers.predicates.encoding,encoding))
        self._add_triples(triples)
        
    def add_component_definition(self,uri,type,role=None,components=[],sas=[],sequence=None,properties={}):
        if not isinstance(uri,URIRef):
            uri = URIRef(uri)
        triples = self._generic_generation(uri,identifiers.objects.component_definition)
        triples.append((uri,identifiers.predicates.type,type))
        if role is not None:
            triples.append((uri,identifiers.predicates.role,role))
        if sequence is not None:
            triples.append((uri,identifiers.predicates.sequence,sequence))
        for component in components:
            triples.append((uri,identifiers.predicates.component,URIRef(component)))
        
        for sa in sas:
            triples.append((uri,identifiers.predicates.sequence_annotation,URIRef(sa)))
        for k,v in properties.items():
            triples.append((uri,URIRef(k),v))
        self._add_triples(triples)

    def add_interaction(self,uri,type,parts={},properties={}):
        if not isinstance(uri,URIRef):
            uri = URIRef(uri)
        triples = self._generic_generation(uri,identifiers.objects.interaction)
        triples.append((uri,identifiers.predicates.type,type))
        for fc,part_type in parts.items():
            part = self.create_part_name(uri,fc.get_key(),fc.get_type())
            triples += self.participation(part,fc.get_key(),part_type)
            triples.append((uri,identifiers.predicates.participation,part))
        for k,v in properties.items():
            triples.append((uri,k,v))
        self._add_triples(triples)

    def add_component(self,uri,definition,parent=None):
        triples = self._generic_generation(uri,identifiers.objects.component)
        triples.append((uri,identifiers.predicates.definition,definition))
        triples.append((uri,identifiers.predicates.access,identifiers.objects.public))
        if parent is not None:
            triples.append((parent,identifiers.predicates.component,uri))
        self._add_triples(triples)

    def add_module_definition(self,uri,modules=[],interactions={}):
        triples = self._generic_generation(uri,identifiers.objects.module_definition)
        for module in modules:
            module = URIRef(module)
            definition = self.create_md_name(module)
            m_uri = self.build_children_uri(uri,module)
            triples += self.module(m_uri,definition)
            triples.append((uri,identifiers.predicates.module,m_uri))
        for i,(i_type,parts,props) in interactions.items():
            interaction = self.build_children_uri(uri,i)
            triples.append((uri,identifiers.predicates.interaction,interaction))
            participants = {}
            for cd,part_type in parts.items():
                cd_key = URIRef(cd.get_key())
                fc = self.create_fc_name(uri,cd_key)
                cd.key = fc
                triples += self.functional_component(fc,cd_key)
                triples.append((uri,identifiers.predicates.functional_component,fc))
                participants[cd] = part_type
            triples += self.interaction(interaction,i_type,participants,props)
        self._add_triples(triples)


    def add_module(self,uri,definition):
        triples = self._generic_generation(uri,identifiers.objects.module)
        triples.append((uri,identifiers.predicates.definition,definition))
        self._add_triples(triples)

    def add_participation(self,uri,fc,part_type,parent=None):
        if not isinstance(fc,(URIRef,BNode)):
            fc = URIRef(fc)
        triples = self._generic_generation(uri,identifiers.objects.participation)
        triples.append((uri,identifiers.predicates.role,part_type))
        triples.append((uri,identifiers.predicates.participant,fc))
        if parent is not None:
            triples.append((URIRef(parent),identifiers.predicates.participation,uri))
        self._add_triples(triples)

    def add_functional_component(self,uri,definition,parent=None):
        triples = self._generic_generation(uri,identifiers.objects.functional_component)
        triples.append((uri,identifiers.predicates.definition,URIRef(definition)))
        triples.append((uri,identifiers.predicates.access,identifiers.objects.public))
        triples.append((uri,identifiers.predicates.direction,identifiers.objects.inout))
        if parent is not None:
            triples.append((parent,identifiers.predicates.functional_component,uri))
        self._add_triples(triples)

    def add_sequence_annotation(self,uri,start,end,strand,component=None):
        triples = self._generic_generation(uri,identifiers.objects.sequence_annotation)
        r_uri = self.build_children_uri(uri,f'{uri[0:-2]}_range/1')
        triples += self.range(r_uri,start,end,strand)
        triples.append((uri,identifiers.predicates.location,r_uri))
        if component is not None:
            triples.append((uri,identifiers.predicates.component,component))
        self._add_triples(triples)

    def add_range(self,uri,start,end,strand):
        triples = self._generic_generation(uri,identifiers.objects.range)
        triples.append((uri,identifiers.predicates.start,start))
        triples.append((uri,identifiers.predicates.end,end))
        triples.append((uri,identifiers.predicates.orientation,strand))
        self._add_triples(triples)


    def remove_component_definition(self,subject):
        for seq in self.get_sequence_names(subject):
            if len(self.search((None,identifiers.predicates.sequence,seq))) == 1:
                self.remove_sequence(seq)
        for sa in self.get_sequence_annotations(subject):
            self.remove_sequence_annotation(sa)
        for sc in self.get_sequence_constraints(subject):
            self.remove_sequence_constraint(sc)
        for c in self.get_heirachical_instances(subject):
            self.remove_component(c)
        for fc in self.get_functional_instances(subject):
            self.remove_functional_component(fc)
        self._remove_triples(self.search((subject,None,None)))

    def remove_component(self,subject):
        self._remove_triples(self.search((subject,None,None)))
        self._remove_triples(self.search((None,identifiers.predicates.component,subject)))

    def remove_functional_component(self,subject):
        self._remove_triples(self.search((subject,None,None)))
        self._remove_triples(self.search((None,identifiers.predicates.functional_component,subject)))

    def remove_sequence(self,subject):
        self._remove_triples(self.search((subject,None,None)))

    def remove_sequence_annotation(self,subject):
        self._remove_triples(self.search((subject,None,None)))

    def remove_sequence_constraint(self,subject):
        self._remove_triples(self.search((subject,None,None)))

    def remove_interaction(self,subject):
        for part in self.get_participants(interaction=subject):
            self.remove_participants(part)
        self._remove_triples(self.search((subject,None,None)))
        
    def remove_participants(self,subject):
        fc = self.get_participant(subject)
        if len(self.search((None,identifiers.predicates.participant,fc))) == 1:
            self.remove_functional_component(fc)
        self._remove_triples(self.search((subject,None,None)) + self.search((None,None,subject)) )

    def build_children_uri(self,base,addition):
        return URIRef(f'{_get_pid(base)}/{_get_name(addition)}/1')

    def create_md_name(self,uri):
        return URIRef(f'{_get_pid(uri)}_md/1')

    def create_sequence_name(self,uri):
        return URIRef(f'{_get_pid(uri)}_sequence/1')

    def create_fc_name(self,int,cd):
        return URIRef(self.build_children_uri(int,_get_name(cd)+"_fc"))

    def create_part_name(self,int,cd,part_type): # Part type is CD type.
        return URIRef(self.build_children_uri(int,f'{_get_name(cd)}_{_get_name(part_type)}'))

def _get_pid(subject):
    if subject[-1].isdigit():
        return URIRef(subject[:-2])

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