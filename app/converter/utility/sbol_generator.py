from rdflib import RDF,Literal,URIRef,DCTERMS
import re
from app.converter.utility.identifiers import identifiers


class SBOLGenerator:
    def __init__(self):
        pass

    def _generic_generation(self,uri,type):
        if not isinstance(uri,URIRef):
            uri = URIRef(uri)
        triples = [(uri,RDF.type,type)]
        triples.append((uri,identifiers.predicates.persistent_identity,_get_pid(uri)))
        triples.append((uri,identifiers.predicates.display_id,Literal(_get_name(uri))))
        triples.append((uri,identifiers.predicates.version,Literal(1)))
        return triples

    def sequence(self,uri,sequence,encoding):
        triples = self._generic_generation(uri,identifiers.objects.sequence)
        triples.append((uri,identifiers.predicates.elements,sequence))
        triples.append((uri,identifiers.predicates.encoding,encoding))
        return triples
        
    def component_definition(self,uri,type,role=None,components=[],sas=[],properties={}):
        if not isinstance(uri,URIRef):
            uri = URIRef(uri)
        triples = self._generic_generation(uri,identifiers.objects.component_definition)
        triples.append((uri,identifiers.predicates.type,type))
        if role is not None:
            triples.append((uri,identifiers.predicates.role,role))
        for component in components:
            triples.append((uri,identifiers.predicates.component,URIRef(component)))
        
        for sa in sas:
            triples.append((uri,identifiers.predicates.sequence_annotation,URIRef(sa)))
        for k,v in properties.items():
            triples.append((uri,k,v))
        return triples

    def component(self,uri,definition):
        triples = self._generic_generation(uri,identifiers.objects.component)
        triples.append((uri,identifiers.predicates.definition,definition))
        triples.append((uri,identifiers.predicates.access,identifiers.objects.public))
        return triples

    def module_definition(self,uri,modules,interactions):
        uri = self.create_md_name(uri)
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
        return triples


    def module(self,uri,definition):
        triples = self._generic_generation(uri,identifiers.objects.module)
        triples.append((uri,identifiers.predicates.definition,definition))
        return triples

    def interaction(self,uri,type,parts,properties={}):
        triples = self._generic_generation(uri,identifiers.objects.interaction)
        triples.append((uri,identifiers.predicates.type,type))
        for fc,part_type in parts.items():
            part = self.create_part_name(uri,fc.get_key(),fc.get_type())
            triples += self.participation(part,fc.get_key(),part_type)
            triples.append((uri,identifiers.predicates.participation,part))
        for k,v in properties.items():
            triples.append((uri,k,v))
        return triples

    def participation(self,uri,fc,part_type):
        triples = self._generic_generation(uri,identifiers.objects.participation)
        triples.append((uri,identifiers.predicates.role,part_type))
        triples.append((uri,identifiers.predicates.participant,URIRef(fc)))
        return triples

    def functional_component(self,uri,definition):
        triples = self._generic_generation(uri,identifiers.objects.functional_component)
        triples.append((uri,identifiers.predicates.definition,URIRef(definition)))
        triples.append((uri,identifiers.predicates.access,identifiers.objects.public))
        triples.append((uri,identifiers.predicates.direction,identifiers.objects.inout))
        return triples

    def sequence_annotation(self,uri,start,end,strand,component=None):
        triples = self._generic_generation(uri,identifiers.objects.sequence_annotation)
        r_uri = self.build_children_uri(uri,f'{uri[0:-2]}_range/1')
        triples += self.range(r_uri,start,end,strand)
        triples.append((uri,identifiers.predicates.location,r_uri))
        if component is not None:
            triples.append((uri,identifiers.predicates.component,component))
        return triples

    def range(self,uri,start,end,strand):
        triples = self._generic_generation(uri,identifiers.objects.range)
        triples.append((uri,identifiers.predicates.start,start))
        triples.append((uri,identifiers.predicates.end,end))
        triples.append((uri,identifiers.predicates.orientation,strand))
        return triples

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