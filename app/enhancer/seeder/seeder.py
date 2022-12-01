import os
import re
from rdflib import URIRef
from rdflib import RDF
from rdflib import DCTERMS
import requests
import atexit
import json
import inspect
from Bio import Align
from Bio.Seq import Seq
from app.converter.utility.common import map_to_nv, get_interaction_properties
from app.graph.utility.model.model import model
from app.graph.utility.graph_objects.node import Node
from app.graph.utility.graph_objects.edge import Edge
from app.converter.utility.graph import SBOLGraph
from  app.converter.utility.identifiers import identifiers as ids


igem_cds = os.path.join(os.path.dirname(os.path.realpath(__file__)),"igem_cds.json")
sbh_igem =  os.path.join(os.path.dirname(os.path.realpath(__file__)),"sbh_igem.xml")
cello_vpr_fn = os.path.join(os.path.dirname(os.path.realpath(__file__)),"cello_vpr.xml")
manual_log_fn = os.path.join(os.path.dirname(os.path.realpath(__file__)),"manual_log.json")

igem_fasta = "http://parts.igem.org/fasta/parts/All_Parts"
cello_parts_old_prefix = "https://synbiohub.programmingbiology.org/public/Cello_Parts/"
cello_parts_new_prefix = "https://synbiohub.programmingbiology.org/public/GokselEco1C1G1T2/"
sbh_igem_prefix = "https://synbiohub.org/public/igem/"

aligner = Align.PairwiseAligner()
aligner.mode = 'global'
aligner.substitution_matrix = Align.substitution_matrices.load("BLOSUM62")
aligner.match_score = 1.0 
aligner.mismatch_score = -1.0
threshold = 0.7

nv_role = model.identifiers.predicates.role
nv_characteristic = model.identifiers.predicates.hasCharacteristic
physical_entity = model.identifiers.roles.physical_entity
interaction = model.identifiers.roles.interaction
p_synonym = model.identifiers.external.synonym
p_similar = model.identifiers.external.similar_to
manual_log = {}
unusable_bl = ["coming soon","coming soon...","tba"]
trash_bl = ["test"]

def exit_handler():
    with open(manual_log_fn, 'w') as f:
        json.dump(manual_log, f)
    manual_log.clear()

atexit.register(exit_handler)

def truth_graph(truth_graph,miner):
    global manual_log
    if os.path.isfile(manual_log_fn):
        with open(manual_log_fn, "r") as json_file:
            manual_log = json.load(json_file)
    if not os.path.isfile(sbh_igem):
        _build_sbol_data(miner)
    _add_sbol_data(truth_graph)

    
def _get_igem_cds():
    if not os.path.isfile(igem_cds):
        qry = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX sbh: <http://wiki.synbiohub.org/wiki/Terms/synbiohub#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX sbol: <http://sbols.org/v2#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX purl: <http://purl.obolibrary.org/obo/>
        PREFIX igem: <http://wiki.synbiohub.org/wiki/Terms/igem#>
        PREFIX igem_pt: <http://wiki.synbiohub.org/wiki/Terms/igem#partType/>
		PREFIX igem_ex: <http://wiki.synbiohub.org/wiki/Terms/igem#experience/>

        SELECT  distinct ?subject
        WHERE {
        ?subject rdf:type sbol:ComponentDefinition .
        ?comon sbol:definition ?subject .
        ?subject igem:discontinued "false" .
        ?subject sbol:sequence ?seq_n .
        ?seq_n sbol:elements ?sequence .
        FILTER( strlen( ?sequence ) > 1 ) .
        FILTER ((STRSTARTS(str(?subject), "https://synbiohub.org/public/igem/")))
        MINUS {?subject sbol:component ?comp .} 
        MINUS {?subject sbol:role igem_pt:Composite .}
        MINUS {?subject sbol:role igem_pt:Device .}
        MINUS {?subject sbol:role igem_pt:Temporary .}
        MINUS {?subject sbol:role igem_pt:Conjugation .}
        MINUS {?subject sbol:role igem_pt:Protein_Domain .} 
        MINUS {?subject sbol:role igem_pt:Other .}
        MINUS {?subject sbol:role igem_pt:Project .}
        MINUS {?subject sbol:role igem_pt:Cell .}
        MINUS {?subject sbol:role igem_pt:Basic .}
        MINUS {?subject sbol:role igem_pt:Intermediate .}
        MINUS {?subject sbol:role igem_pt:Plasmid .}
        MINUS {?subject sbol:role igem_pt:Plasmid_Backbone .}
        MINUS {?subject sbol:role igem_pt:Primer .}
        MINUS {?subject sbol:role igem_pt:Measurement .}
        MINUS {?subject sbol:role igem_pt:Tag .}
        MINUS {?subject igem:experience igem_ex:Fails .}
        MINUS {?subject igem:experience igem_ex:Issues .}
        }
        """
        qry = requests.utils.quote(qry)
        response = requests.get(
            f'https://synbiohub.org/sparql?query={qry}',
            headers={'Accept': 'application/json'})
        response = json.loads(response.content)
        items = [r["subject"]["value"] for r in response["results"]["bindings"]]
        with open(igem_cds, "w") as f:    
            f.write(json.dumps(items))
        
    with open(igem_cds) as f:
        return json.load(f)
            

def _build_sbol_data(miner):
    igem_cds = _get_igem_cds()
    if not os.path.isfile(cello_vpr_fn):
        _build_cello_vpr(miner)
    c_vpr_graph = SBOLGraph(cello_vpr_fn)
    c_parts = {}

    for cd in c_vpr_graph.get_component_definitions():
        seq = c_vpr_graph.get_sequences(cd)
        md = c_vpr_graph.get_metadata(cd)
        c_parts[cd] = {}
        if seq != []:
            seq = seq[0]
        else:
            seq = None
        c_parts[cd]["seq"] = seq
        c_parts[cd]["meta"] = md
        c_parts[cd]["types"] = c_vpr_graph.get_types(cd)
        c_parts[cd]["roles"] = c_vpr_graph.get_roles(cd)

    graph = SBOLGraph()
    last_sequence = ""
    last_id = ""
    matches = []
    for index,cd in enumerate(igem_cds):
        cd = URIRef(cd)
        record = SBOLGraph(miner.get_external(cd,timeout=80))
        print("\n")
        print(f'{str(index/len(igem_cds) * 100)}%')
        print(cd)
        md = record.get_metadata(cd)
        # IGEM -> IGEM-SBH
        record = SBOLGraph(miner.get_external(cd,timeout=80))
        if record is None:
            continue
        sequence = record.get_sequences(cd)
        md = record.get_metadata(cd)
        if _is_trash(md,sequence):
            continue
        sequence = sequence[0]
        if str(last_sequence) == str(sequence):
            graph.add_triple((last_id,ids.predicates.synonym,cd))
            continue
        if _has_components(cd,record):
            continue
        graph += _prune_igem_graph(record)
        roles = record.get_roles(cd)
        # IGEM-SBH + Cello-VPR
        print(md)
        analogue = _derive_cello_analogues(cd,sequence,md,roles,c_parts)
        if analogue is not None:
            print(analogue)
            matches.append((cd,analogue))
        last_id = cd

    while len(matches) > 0:
        ig,lcp = matches.pop(0)
        lcps = [lcp]
        igs = [ig]
        index = 0
        while index < len(matches):
            i,l = matches[index]
            if l == lcp:
                igs.append(i)
                lcps.append(l)
                del matches[index]
            else:
                index += 1

        p = _get_input(int,igs,[f'{ind}: {i}' for ind,i in enumerate(igs)],
                               [i for i in range(0,len(igs))])
        main_ig = igs.pop(p)
        for ig in list(set(igs)):
            graph.add_triple((main_ig,p_similar,ig))
        for lcp in list(set(lcps)):
            c_vpr_graph.remove_properties(lcp,ids.predicates.prune)
            for seq_n in c_vpr_graph.get_sequence_names(lcp):
                if len(c_vpr_graph.get_component_definitions(seq_name=seq_n)) == 1:
                    c_vpr_graph.remove_sequence(seq_n)
                    c_vpr_graph.remove_triple((lcp,ids.predicates.sequence,seq_n))
            graph.add_triple((main_ig,p_synonym,lcp))
            c_vpr_graph.replace_uri(lcp,main_ig)
    graph += c_vpr_graph
    graph.save(sbh_igem)


def _is_trash(metadata,sequence):
    if len(sequence) != 1:
        return True
    if len(sequence[0]) < 2:
        return True
    if any(ext in trash_bl for ext in metadata):
        return True
    if any(ext in unusable_bl for ext in metadata):
        return True
    return False


def _get_input(domain,vals,message=None,range=None):
    inp = None   
    if message is None:
        message = vals
    message = str(message)
    vals = str(vals)
    caller = inspect.currentframe().f_back.f_code.co_name
    if caller in manual_log and vals in manual_log[caller]:
        return manual_log[caller][vals]
    while inp is None or not isinstance(inp,domain) and range is not None or inp not in range:
        print(inp,range)
        inp = input(message)
        try:
            inp = domain(inp)
        except Exception:
            pass

    if caller in manual_log:
        manual_log[caller][vals] = inp
    else:
        manual_log[caller] = {vals : inp}
    return inp


def _add_sbol_data(tg):
    model_roots = model.get_base_class()
    graph = SBOLGraph(sbh_igem)
    object_type_map = {}
    # Does the Interaction Exists?
    # Does a Node with the same type (Not key) exist 
    # with edges (of same type) and same cd nodes.
    seen_interactions = []
    interactions = []
    for i in graph.get_interactions():
        participants = []
        i_type = graph.get_type(i)
        for p in graph.get_participants(interaction=i):
            p_type = frozenset(graph.get_roles(p))
            fc = graph.get_participant(p)
            participants.append(frozenset([graph.get_definition(fc),p_type]))
        participants = frozenset(participants)
        coll = frozenset([i_type,participants])
        if coll in seen_interactions:
            continue
        else:
            seen_interactions.append(coll)
            interactions.append(i)


    def _add_node(name, type=None, props=None):
        properties = _get_properties(name, graph)
        if props is not None:
            properties.update(props)
        neo = tg.add_node(Node(name,type,**properties))
        return neo

    def _add_edge(n, v, e):
        properties = _get_properties(e, graph)
        tg.add_edge(Edge(n,v,str(e),**properties),5)

    for cd in graph.get_component_definitions():
        properties = ([(nv_characteristic, physical_entity)] +
                      [(nv_role, r) for r in (graph.get_roles(cd)+graph.get_types(cd))])

        s, p, o = map_to_nv(cd, properties, model_roots, model)
        sequence = graph.get_sequences(cd)
        if len(sequence) > 0:
            assert(len(sequence) == 1)
            props = {model.identifiers.predicates.hasSequence: sequence[0]}
        else:
            props = None
        n = _add_node(s, o, props)
        object_type_map[s] = o
        for s,p,o in graph.search((cd,[p_synonym,p_similar],None)):
            o = _add_node(o)
            _add_edge(n, o, p)

    for i in interactions:
        roles = ([(nv_characteristic, interaction)] +
                 [(nv_role, r) for r in (graph.get_types(i))])
        s, p, o = map_to_nv(i, roles, model_roots, model)

        n = _add_node(s, o)
        for s, p, o in get_interaction_properties(i, o, object_type_map, model, graph,add_nv_props=False):
            if p == RDF.type:
                s = _add_node(s, o)
            else:
                s = _add_node(s)
                o = _add_node(o)
                _add_edge(s, o, p)


def _has_components(subject,graph):
    component_roles = [
                       ids.roles.rbs,
                       ids.roles.cds,
                       ids.roles.terminator,
                       ids.roles.igem_rbs,
                       ids.roles.igem_cds,
                       ids.roles.igem_terminator,
                       ids.roles.igem_protein]
    # IGEM -> SBH has some components as annotations 
    # which should be components. They have roles such as CDS.
    instance_count = 0
    for sa in graph.get_sequence_annotations(subject):
        roles = graph.get_roles(sa)
        if len(list(set(roles) & set(component_roles))) > 0:
            instance_count += 1
            if instance_count > 1:
                return True
    return False
    

def _derive_cello_analogues(name,seq,metadata,roles,cello_cds):
    s_seq = Seq(seq.lower())
    for cd,c_data in cello_cds.items():
        c_seq = c_data["seq"]
        c_md = c_data["meta"]
        c_types = c_data["types"]
        c_roles = c_data["roles"]
        if ids.roles.DNA not in c_types and ids.roles.DNARegion not in c_types:
            continue
        if len(roles) > 0 and len(c_roles) > 0 and len(list(set(roles) & set(c_roles))) == 0:
            continue
        if c_seq is not None:
            seq1 = Seq(c_seq.lower())
            score = aligner.score(s_seq,seq1)/len(max([s_seq,seq1], key=len))
            if score == 1.0:
                return cd
            if score > threshold:
                print(f"By Sequence: {score}")
                print(f'http://parts.igem.org/Part:{_get_name(name)}',cd)
                print(s_seq,seq1)
                if _get_input(str,f'{name} - {cd}',range=["y","n"]) == "y":
                    return cd
        for d in c_md:
            if any(ext in d for ext in metadata):
                print(f"By Metadata: {metadata}")
                print(f'http://parts.igem.org/Part:{_get_name(name)}',cd)
                print(s_seq,seq1)
                if _get_input(str,f'{name} - {cd}',range=["y","n"]) == "y":
                    return cd 
    return None


def _build_cello_vpr(miner):
    n_c_parts = SBOLGraph(miner.get_external("GokselEco1C1G1T2_collection",timeout=80))
    graph = SBOLGraph(miner.get_external("Cello_Parts_collection",timeout=80) + 
                      miner.get_external("Cello_VPRGeneration_Paper_collection",timeout=80))
    new_cds = n_c_parts.get_component_definitions()
    for cd in graph.get_component_definitions():
        name = _get_name(cd)
        p_new_uri = URIRef(cello_parts_new_prefix+name+"/1") 
        if p_new_uri in new_cds:
            graph.replace_component_definition(cd,p_new_uri)
    for m in graph.get_maps_to():
        l_fc = graph.get_local(m)
        r_fc = graph.get_remote(m)
        l = graph.get_definition(l_fc)
        r = graph.get_definition(r_fc)
        if l == r:
            continue
        else:
            if cello_parts_new_prefix in l or cello_parts_old_prefix in l:
                graph.replace_triple((r_fc,ids.predicates.definition,r),
                                     (r_fc,ids.predicates.definition,l))
                graph.remove_component_definition(r)

            elif cello_parts_new_prefix in r or cello_parts_old_prefix in r:
                graph.replace_triple((l_fc,ids.predicates.definition,l),
                                     (l_fc,ids.predicates.definition,r))
                graph.remove_component_definition(l)
            else:
                raise ValueError(l,r)
        graph.remove_maps_to(m)

    graph = _prune_igem_graph(graph)
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
    
    # Weirdness with the VPR model.
    # They encode certain interactions between abstraction (Protein - Repress - Construct for example.)
    for cd in graph.get_component_definitions():
        comps = graph.get_components(cd)
        if len(comps) == 0:
            continue
        fis = graph.get_functional_instances(cd)
        if len(fis) == 0:
            graph.remove_component_definition(cd)
            continue
        cts = {}
        for c in comps:
            c_def = graph.get_definition(c)
            for r in graph.get_roles(c_def):
                if r in cts:
                    cts[r].append(c_def)
                else:
                    cts[r] = [c_def]
        del comps
        for fc in fis:
            for p_part in graph.get_participants(fc=fc):
                p_role = graph.get_roles(p_part)  
                for i in graph.get_interactions(participation=p_part):
                    i_type = graph.get_type(i)
                    if i_type == ids.roles.inhibition and ids.roles.inhibited in p_role:
                        # Protein - Inhibit - Gene -> Protein - Inhibit -> Promoter
                        graph = _replace(graph,i,p_part,fc,cts,ids.roles.promoter)
                    elif i_type == ids.roles.genetic_production and ids.roles.template in p_role:
                        # Gene - Produces - Protein -> CDS - Produces - Protein
                        graph = _replace(graph,i,p_part,fc,cts,ids.roles.cds)
                    elif i_type == ids.roles.stimulation and ids.roles.stimulated in p_role:
                        # Complex - Activates - Gene -> Complex - Activates - Promoter
                        graph = _replace(graph,i,p_part,fc,cts,ids.roles.promoter)
                    else:
                        raise ValueError(f'{i_type} - {p_role}')
        graph.remove_component_definition(cd)
    graph.save(cello_vpr_fn)


def _replace(graph,i,p_part,fc,cts,role):
    a_parts = graph.get_participants(interaction=i)
    a_parts.remove(p_part)
    assert(len(a_parts) == 1)
    a_parts = a_parts[0]
    assert(role in cts)
    for entity in cts[role]:
        name = _get_name(entity)
        if name in p_part:
            replacement = entity
            break
    else:
        replacement = cts[_get_input(str,cts[role])]
    md = graph.get_module_definition(interaction=i)
    fc_n = graph.create_fc_name(md,replacement)
    graph.add_functional_component(fc_n,replacement,md)
    graph.replace_triple((p_part,ids.predicates.participant,fc),
                         (p_part,ids.predicates.participant,fc_n))
    return graph


def _prune_igem_graph(graph):
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
    "experience"]
    prune_preds = [(None,getattr(ids.predicates,p),None) for p in preds]
    for triple in prune_preds:
        graph.remove_triple(triple)
    return graph


def _get_properties(entity, graph):
    properties = {}
    meta = graph.get_metadata(entity)
    properties["name"] = _get_name(entity)
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