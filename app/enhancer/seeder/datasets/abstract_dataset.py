from abc import ABC, abstractmethod
import re
from rdflib import URIRef, RDF, DCTERMS
from  app.converter.utility.identifiers import identifiers as ids
from app.converter.utility.common import map_to_nv, get_interaction_properties
from app.graph.utility.model.model import model
from app.graph.utility.graph_objects.edge import Edge

nv_role = model.identifiers.predicates.role
nv_characteristic = model.identifiers.predicates.hasCharacteristic
physical_entity = model.identifiers.roles.physical_entity
r_interaction = model.identifiers.roles.interaction
p_synonym = model.identifiers.external.synonym
p_similar = model.identifiers.external.similar_to
o_interaction = model.identifiers.objects.interaction

unusable_bl = ["coming soon","coming soon...","tba"]
trash_bl = ["test"]

class AbstractDatabase(ABC):
    def __init__(self,graph,miner,aligner):
        self._graph = graph
        self._miner = miner
        self._aligner = aligner

    @abstractmethod
    def build(self):
        pass

    @abstractmethod
    def integrate(self,graph,threshold,existing_seqs=None,existing_ints=None,existing_non_dna=None):
        model_roots = model.get_base_class()
        o_type_map = {}
        if existing_seqs is None:
            existing_seqs = {}
        if existing_ints is None:
            existing_ints = {}
        if existing_non_dna is None:
            existing_non_dna = {}
        dups = []
        sims = []
        dup_i = []
        for cd in graph.get_component_definitions():
            cd_types = graph.get_types(cd)
            if ids.roles.DNARegion in cd_types or ids.roles.DNA in cd_types:
                cd_seq = graph.get_sequences(cd)
                assert(len(cd_seq) == 1)
                cd_seq = cd_seq[0].lower()
                if cd_seq in existing_seqs:
                    graph.replace_component_definition(cd,existing_seqs[cd_seq])
                    self._graph.synonyms.positive(existing_seqs[cd_seq],cd)
                    dups.append((existing_seqs[cd_seq],cd))
                    continue
                o_type_map = self._add_cd(cd,graph,cd_types,model_roots,o_type_map)
                highest_score = [0,None]
                for k,v in existing_seqs.items():
                    score = self._aligner.sequence_match(k,cd_seq)
                    if score > highest_score[0]:
                        highest_score = [score,v]
                if highest_score[0] > threshold:
                    sims.append((highest_score[1],cd))
                    self._graph.derivatives.positive(highest_score[1],cd,highest_score[0])
                existing_seqs[cd_seq] = cd
            else:
                cd_name = self._get_name(cd)
                for e,e_types in existing_non_dna.items():
                    if len(list(set(e_types) & set(cd_types))) == 0:
                        continue
                    name = self._get_name(e)
                    if cd_name in name or name in cd_name:
                        self._graph.synonyms.positive(e,cd)
                        dups.append((e,cd))
                        break
                else:
                    o_type_map = self._add_cd(cd,graph,cd_types,model_roots,o_type_map)
                    existing_non_dna[cd] = cd_types
        
        for i in graph.get_interactions():
            i_type = graph.get_types(i)
            e_parts = []
            for p in graph.get_participants(interaction=i):
                p_role = graph.get_roles(p)
                assert(len(p_role) == 1)
                fc = graph.get_participant(p)
                fc_def = graph.get_definition(fc)
                e_parts.append(f'{p_role[0]}{fc_def}')
            
            assert(len(i_type) == 1)
            i_type = i_type[0]
            if i_type in existing_ints:
                for i_parts in existing_ints[i_type]:
                    if e_parts == i_parts:
                        dup_i.append(i)
                        break
                else:
                    self._add_interaction(i,graph,model_roots,o_type_map)
                    existing_ints[i_type] += [e_parts]
            else:
                self._add_interaction(i,graph,model_roots,o_type_map)
                existing_ints[i_type] = [e_parts]
                
        print(len(dups),len(sims))
        print("Duplicates:")
        for d in dups:
            print(d)
        print("Similars:")
        for e in sims:
            print(e)
        print("Redundant Interactions:")
        for i in dup_i:
            print(i)
        return existing_seqs,existing_ints,existing_non_dna

    
    def _add_cd(self,cd,s_graph,cd_types,m_roots,type_map):
        properties = ([(nv_characteristic, physical_entity)] +
                    [(nv_role, r) for r in (s_graph.get_roles(cd) + cd_types)])
        s, p, o = map_to_nv(cd, properties, m_roots, model)
        sequence = s_graph.get_sequence_names(cd)
        if len(sequence) > 0:
            assert(len(sequence) == 1)
            props = {model.identifiers.predicates.hasSequence: sequence[0]}
        else:
            props = None
        n = self._add_node(s_graph,s, o, props)
        type_map[s] = o
        for s,p,o in s_graph.search((cd,[p_synonym,p_similar],None)):
            o = self._add_node(s_graph,o)
            self._graph.synonyms.positive(n,o)
        return type_map


    def _add_interaction(self,i,s_graph,m_roots,type_map):
        roles = ([(nv_characteristic, r_interaction)] +
                [(nv_role, r) for r in (s_graph.get_types(i))])
        s, p, o = map_to_nv(i, roles, m_roots, model)
        if o == o_interaction:
            return
        n = self._add_node(s_graph,s, o)
        for s, p, o in get_interaction_properties(i, o, type_map, model, s_graph,add_nv_props=False):
            if p == RDF.type:
                s = self._add_node(s_graph,s, o)
            else:
                s = self._add_node(s_graph,s)
                o = self._add_node(s_graph,o)
                self._add_edge(s_graph,s, o, p)


    def _add_node(self,graph,name, type=None, props=None):
        properties = self._get_properties(name, graph)
        if props is not None:
            properties.update(props)
        neo = self._graph.add_node(name,type,**properties)
        return neo


    def _add_edge(self,graph,n, v, e):
        properties = self._get_properties(e, graph)
        self._graph.add_edges(Edge(n,v,str(e),**properties),5)


    def _get_properties(self,entity, graph):
        properties = {}
        meta = graph.get_metadata(entity)
        properties["name"] = self._get_name(entity)
        if len(meta) > 0:
            properties[DCTERMS.description] = meta
        return properties


    def _replace_cd(sel,graph,replacer,replaced):
        graph.remove_triple((replaced,ids.predicates.title,None))    
        for sa in graph.get_sequence_annotations(replaced):
            graph.remove_sequence_annotation(sa)
        for seq in graph.get_sequence_names(replaced):
            graph.remove_sequence(seq)
        graph.replace_component_definition(replaced,replacer)
        graph.add_synonym(replacer,replaced)
        return graph


    def _is_trash(self,metadata,sequence):
        if len(sequence) != 1:
            return True
        if len(sequence[0]) < 2:
            return True
        if any(ext in trash_bl for ext in metadata):
            return True
        if any(ext in unusable_bl for ext in metadata):
            return True
        return False
    

    def _prune_sbol_predicates(self,graph):
        preds = [
        "toplevel",
        "ownedby",
        "created",
        "was_generated_by",
        "ended_at_time",
        "had_plan",
        "entity",
        "qualified_association",
        "qualified_usage",
        "agent",
        "model",
        "bookmark",
        "star",
        "modified",
        "owning_group_id",
        "dominant",
        "creator",
        "wasDerivedFrom",
        "bookmark",
        "m_user_id",
        "group_u_list",
        "owner_id",
        "status",
        "sampleStatus",
        "experience",
        "direction",
        "igdirection",
        "partStatus",
        "discontinued"]
        prune_preds = [(None,getattr(ids.predicates,p),None) for p in preds]
        for triple in prune_preds:
            graph.remove_triple(triple)
        return graph
    

    def _prune_sbol_objects(self,graph):
        pruned_objs = [ids.objects.collection,
                    ids.objects.attachment,
                    ids.objects.model,
                    ids.objects.activity,
                    ids.objects.usage,
                    ids.objects.association,
                    ids.objects.agent,
                    ids.objects.plan]
        for s,p,o in graph.search((None,RDF.type,pruned_objs)):
            graph.remove_triple((s,None,None))
        return graph
    

    def _handle_component_definition(self,graph,cd,seqs):
        md = graph.get_metadata(cd)
        sequence = graph.get_sequences(cd)
        if self._is_trash(md,sequence):
            return None,seqs
        if self._has_components(cd,graph):
            return None,seqs
        graph = self._prune_sbol_predicates(graph)
        graph = self._prune_sbol_objects(graph)
        seq = graph.get_sequences(cd)
        assert(len(seq) == 1)
        seq = seq[0]
        if seq in seqs:
            graph = self._replace_cd(graph,URIRef(seqs[seq]),cd)
        else:
            seqs[seq] = cd
        return graph,seqs


    def _has_components(self,subject,graph):
        component_roles = [
                        ids.roles.promoter,
                        ids.roles.rbs,
                        ids.roles.cds,
                        ids.roles.terminator,
                        ids.roles.igem_promoter,
                        ids.roles.igem_rbs,
                        ids.roles.igem_cds,
                        ids.roles.igem_terminator,
                        ids.roles.igem_protein]
        # IGEM -> SBH has some components as annotations 
        # which should be components. They have roles such as CDS.
        instance_count = 0
        for c in graph.get_components(subject):
            c_def = graph.get_definition(c)
            roles = graph.get_roles(c_def)
            if len(list(set(roles) & set(component_roles))) > 0:
                instance_count += 1
                if instance_count > 1:
                    return True
                
        for sa in graph.get_sequence_annotations(subject):
            roles = graph.get_roles(sa)
            if len(list(set(roles) & set(component_roles))) > 0:
                instance_count += 1
                if instance_count > 1:
                    return True
        return False
    

    def _replace(self,graph,i,p_part,fc,cts,role):
        a_parts = graph.get_participants(interaction=i)
        a_parts.remove(p_part)
        assert(len(a_parts) == 1)
        a_parts = a_parts[0]
        assert(role in cts)
        for entity in cts[role]:
            name = self._get_name(entity)
            if name in p_part:
                replacement = entity
                break
        else:
            raise ValueError()
            #replacement = cts[_get_input(str,cts[role])]
        md = graph.get_module_definition(interaction=i)
        fc_n = graph.create_fc_name(md,replacement)
        graph.add_functional_component(fc_n,replacement,md)
        graph.replace_triple((p_part,ids.predicates.participant,fc),
                            (p_part,ids.predicates.participant,fc_n))
        return graph
    

    def _role_intersection(self,r1s,r2s):
        if len(r1s) > 0 and len(r2s) > 0 and len(list(set(r1s) & set(r2s))) == 0:
            return True
        return False
    

    def _get_name(self,subject):
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