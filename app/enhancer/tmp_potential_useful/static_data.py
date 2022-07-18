from rdflib import Literal,URIRef
import enchant

from graph.knowledge.utility.identifiers import identifiers
from utility.sbol_identifiers import identifiers as sbol_identifiers
'''
Manually curated structures for the knowledge graph.
Only used if for some reason the knowledge graph is lost.
'''
def produce_triples():
    triples = []
    to_calls = [produce_identifier_map_triples,
                produce_interaction_tag_map,
                produce_object_alias_triples,
                produce_interaction_alias_triples,
                produce_common_object_triples,
                produce_common_interaction_triples]

    for func in to_calls:
        triples = triples + func()
    return triples

def produce_identifier_map_triples():
    triples = []
    for o_id,kg_id in identifier_map.items():
        triples.append((o_id,identifiers.predicates.rdf_type,identifiers.objects.descriptor_type))
        triples.append((o_id,identifiers.predicates.predicate_map,kg_id))
    return triples

def produce_interaction_tag_map():
    triples = []
    for s,p,o in interaction_tag_list:
        if s is not None:
            if isinstance(s,(list,tuple,set)):
                for tag in s:
                    triples.append((p,identifiers.predicates.interaction_subject,tag))
            else:
                triples.append((p,identifiers.predicates.interaction_subject,s))
        if o is not None:
            if isinstance(o,(list,tuple,set)):
                for tag in o:
                    triples.append((p,identifiers.predicates.interaction_object,tag))
            else:
                triples.append((p,identifiers.predicates.interaction_object,o))
    return triples
    
def produce_common_object_triples():
    triples = []
    for name,data in common_object.items():
        triples.append((name,identifiers.predicates.rdf_type,identifiers.objects.entity_type))
        triples.append((name,identifiers.predicates.alias,Literal(_get_name(name))))
        if identifiers.predicates.role in data.keys():
            role = data[identifiers.predicates.role]
            if len(role) == 1:
                a_name = f'{_get_name(name)}_{_get_name(role[0])}'.lower()
                triples.append((name,identifiers.predicates.alias,Literal(a_name)))
            elif len(role) == 2:
                aname = sbol_identifiers.external.cd_role_dict[role[0]][role[1]]
                a_name = f'{_get_name(name)}_{aname}'.lower()
                triples.append((name,identifiers.predicates.alias,Literal(a_name)))
        for predicate,objects in data.items():
            for obj in objects:
                if isinstance(obj,URIRef):
                    triples.append((name,predicate,obj))
                else:
                    triples.append((name,predicate,Literal(obj.lower())))
    return triples
    
def produce_common_interaction_triples():
    triples = []
    for interaction in common_interactions:
        for i_type, parts in interaction.items():
            subjects = parts["S"]
            objects = parts["O"]
            for subject in subjects:
                triples.append((subject[0],identifiers.predicates.role,subject[1]))
                for obj in objects:
                    triples.append((subject[0],i_type,obj[0]))
                    triples.append((obj[0],identifiers.predicates.role,obj[1]))
                if subject[1] in non_directed_participants:
                    for subject1 in subjects:
                        if subject1 == subject:
                            continue
                        triples.append((subject[0],i_type,subject1[0]))
                        triples.append((subject1[0],i_type,subject[0]))

    return triples

def produce_object_alias_triples():
    triples = []
    for obj_id,aliases in object_aliases.items():
        triples.append((obj_id,identifiers.predicates.rdf_type,identifiers.objects.descriptor_type))
        for alias in aliases:
            triples.append((obj_id,identifiers.predicates.alias,Literal(alias)))
    return triples

def produce_interaction_alias_triples():
    triples = []
    for triple,aliases in interaction_aliases.items():
        s,p,o = triple
        for alias in aliases:
            triples = triples + _produce_subject_triples(s,alias)
            triples = triples + _produce_predicate_triples(p,alias)
            triples = triples + _produce_object_triples(o,alias)
    triples = _prune_triples(triples)
    return triples

def _produce_subject_triples(s,alias):
    interaction_subject_suffixes = ["er","or","ar","ant","ent"]
    return _produce_alias_triples(s,alias,interaction_subject_suffixes)

def _produce_predicate_triples(p,alias):
    interaction_predicate_suffixes = ["s","es","ion","ing"]
    return _produce_alias_triples(p,alias,interaction_predicate_suffixes)

def _produce_object_triples(o,alias):
    interaction_object_suffixes = ["ed","able","ible"]
    return _produce_alias_triples(o,alias,interaction_object_suffixes)

def _produce_alias_triples(uri,alias,suffixes):
    triples = []
    if uri is None:
        return triples
    triples.append((uri,identifiers.predicates.rdf_type,identifiers.objects.descriptor_type))
    for suffix in suffixes:
        triple = (uri,identifiers.predicates.alias,Literal(alias + suffix))
        triples.append(triple)
    return triples

def _prune_triples(triples):
    d_us = enchant.Dict("en_US")
    d_uk = enchant.Dict("en_UK")
    final_triples = []
    for s,p,o in triples:
        if isinstance(o,Literal):
            obj = str(o).split()
            fail = False
            for w in obj: 
                if not d_us.check(w) and not d_uk.check(w):
                    fail = True
                    break
            if not fail:
                final_triples.append((s,p,Literal(o)))
        
        elif isinstance(o,URIRef):
            final_triples.append((s,p,URIRef(o)))
    return final_triples



bio_ns = identifiers.namespaces.knowledge_graph.entity
ptetr = URIRef(bio_ns + "ptetr")
plac = URIRef(bio_ns + "plac")
pveg = URIRef(bio_ns + "pveg")
pbad = URIRef(bio_ns + "pbad")
pluxstar = URIRef(bio_ns + "pluxstar")
plas = URIRef(bio_ns + "plas")
plux = URIRef(bio_ns + "plux")

elowitz_rbs = URIRef(bio_ns + "elowitz_rbs")

tetr = URIRef(bio_ns + "tetr")
laci = URIRef(bio_ns + "laci")
arac = URIRef(bio_ns + "arac")
luxr = URIRef(bio_ns + "luxr")
rhlr = URIRef(bio_ns + "rhlr")
lasr = URIRef(bio_ns + "lasr")

atc = URIRef(bio_ns + "atc")
ara = URIRef(bio_ns + "ara")
iptg = URIRef(bio_ns + "iptg")
hsl = URIRef(bio_ns + "hsl")
rhlahl = URIRef(bio_ns + "rhlahl")
lasahl = URIRef(bio_ns + "lasahl")

ara_arac = URIRef(bio_ns + "ara_arac")
atc_tetr = URIRef(bio_ns + "atc_tetr")
iptg_laci = URIRef(bio_ns + "iptg_laci")
hsl_luxr = URIRef(bio_ns + "hsl_luxr")
rhlahl_rhlr = URIRef(bio_ns + "rhlahl_rhlr")
lasahl_lasr = URIRef(bio_ns + "lasahl_lasr")


common_object = {
    ptetr    :   {identifiers.predicates.alias       : ["ptet","BBa_R0040"],
                  identifiers.predicates.role        : [identifiers.objects.DNA,identifiers.objects.promoter],
                  identifiers.predicates.description : ["constitutively ON","repressed by TetR","pTet inverting regulator"]},

    plac     :   {identifiers.predicates.alias       : ["BBa_K292002"],
                  identifiers.predicates.role        : [identifiers.objects.DNA,identifiers.objects.promoter],
                  identifiers.predicates.description : ["constitutively ON","repressed by LacI"]},

    pveg     :   {identifiers.predicates.alias       : ["BBa_K143012"],
                  identifiers.predicates.role        : [identifiers.objects.DNA,identifiers.objects.promoter],
                  identifiers.predicates.description : ["constitutively ON"]},      

    pbad     :   {identifiers.predicates.alias       : ["BBa_I0500","BBa_K206000"],
                  identifiers.predicates.role        : [identifiers.objects.DNA,identifiers.objects.promoter],
                  identifiers.predicates.description : ["repressed by AraC","activated by arabinose"]},

    pluxstar :   {identifiers.predicates.alias       : ["plux+"],
                  identifiers.predicates.role        : [identifiers.objects.DNA,identifiers.objects.promoter],
                  identifiers.predicates.description : ["constitutively WEAK","activated by hsl + luxr"]},

    plas     :   {identifiers.predicates.alias       : ["BBa_K091117"],
                  identifiers.predicates.role        : [identifiers.objects.DNA,identifiers.objects.promoter],
                  identifiers.predicates.description : ["repressed by LasR","activated by PAI-1"]},

    plux     :   {identifiers.predicates.alias       : ["BBa_R0062"],
                  identifiers.predicates.role        : [identifiers.objects.DNA,identifiers.objects.promoter],
                  identifiers.predicates.description : ["constitutively WEAK","activated by hsl + luxr"]},

    elowitz_rbs :{identifiers.predicates.alias       : ["elowitz","BBa_B0034"],
                  identifiers.predicates.role        : [identifiers.objects.DNA,identifiers.objects.rbs],
                  identifiers.predicates.description : ["RBS based on Elowitz repressilator"]},

    tetr     :   {identifiers.predicates.alias       : ["Tetracycline repressor protein"],
                  identifiers.predicates.role        : [identifiers.objects.protein],
                  identifiers.predicates.description : ["represses ptet", "binds to atc"]},

    laci     :   {identifiers.predicates.alias       : ["Lactose operon repressor"],
                  identifiers.predicates.role        : [identifiers.objects.protein],
                  identifiers.predicates.description : ["represses plac","the Lactose inhibitor","bind to IPTG"]},

    arac     :   {identifiers.predicates.alias       : ["Arabinose operon regulatory protein"],
                  identifiers.predicates.role        : [identifiers.objects.protein],
                  identifiers.predicates.description : ["represses pbad","bind to arabinose"]},

    luxr     :   {identifiers.predicates.alias       : [],
                  identifiers.predicates.role        : [identifiers.objects.protein],
                  identifiers.predicates.description : ["bind to hsl"]},

    rhlr     :   {identifiers.predicates.alias       : [],
                  identifiers.predicates.role        : [identifiers.objects.protein],
                  identifiers.predicates.description : ["bind to rhlahl","binds to Rhl","activates lasB"]},

    lasr     :   {identifiers.predicates.alias       : [],
                  identifiers.predicates.role        : [identifiers.objects.protein],
                  identifiers.predicates.description : ["bind to rhlahl","binds to Rhl"]},

    atc      :   {identifiers.predicates.alias       : ["anhydrotetracycline"],
                  identifiers.predicates.role        : [identifiers.objects.smallMolecule],
                  identifiers.predicates.description : ["binds to tetr"]},

    ara      :   {identifiers.predicates.alias       : ["arabinose"],
                  identifiers.predicates.role        : [identifiers.objects.smallMolecule],
                  identifiers.predicates.description : ["bind to arac"]},

    iptg     :   {identifiers.predicates.alias       : ["Isopropyl β- d-1-thiogalactopyranoside"],
                  identifiers.predicates.role        : [identifiers.objects.smallMolecule],
                  identifiers.predicates.description : ["bind to laci"]},

    hsl      :   {identifiers.predicates.alias       : ["Hormone-sensitive lipase"],
                  identifiers.predicates.role        : [identifiers.objects.smallMolecule],
                  identifiers.predicates.description : ["bind to luxr"]},

    rhlahl   :   {identifiers.predicates.alias       : ["Rhl AHL"],
                  identifiers.predicates.role        : [identifiers.objects.smallMolecule],
                  identifiers.predicates.description : ["bind to lasr"]},

    lasahl   :   {identifiers.predicates.alias       : ["las ahl"],
                  identifiers.predicates.role        : [identifiers.objects.smallMolecule],
                  identifiers.predicates.description : ["bind to lasr"]},

    ara_arac    :   {identifiers.predicates.alias    : ["ara arac"],
                     identifiers.predicates.role     : [identifiers.objects.complex],
                  identifiers.predicates.description : ["ara + arac bound"]},

    atc_tetr    :   {identifiers.predicates.alias    : ["atc tetr"],
                     identifiers.predicates.role     : [identifiers.objects.complex],
                  identifiers.predicates.description : ["atc + tetr bound"]},

    iptg_laci   :   {identifiers.predicates.alias    : ["iptg laci"],
                     identifiers.predicates.role     : [identifiers.objects.complex],
                  identifiers.predicates.description : ["iptg + laci bound"]},

    hsl_luxr    :   {identifiers.predicates.alias    : ["hsl luxr"],
                     identifiers.predicates.role     : [identifiers.objects.complex],
                  identifiers.predicates.description : ["hsl + luxr bound"]},

    rhlahl_rhlr :   {identifiers.predicates.alias    : ["rhlahl rhlr"],
                     identifiers.predicates.role     : [identifiers.objects.complex],
                  identifiers.predicates.description : ["rhlahl + rhlr bound"]},

    lasahl_lasr :   {identifiers.predicates.alias    : ["lasahl lasr"],
                     identifiers.predicates.role     : [identifiers.objects.complex],
                  identifiers.predicates.description : ["lasahl + lasr bound"]},
}

non_directed_participants = [identifiers.objects.reactant] 
common_interactions = [
    {identifiers.predicates.inhibition : {"S": [(atc,identifiers.objects.inhibitor)], 
                                          "O" : [(tetr,identifiers.objects.inhibited)]}},

    {identifiers.predicates.inhibition : {"S": [(tetr,identifiers.objects.inhibitor)], 
                                          "O" : [(ptetr,identifiers.objects.inhibited)]}},

    {identifiers.predicates.inhibition : {"S": [(laci,identifiers.objects.inhibitor)], 
                                          "O" : [(plac,identifiers.objects.inhibited)]}},

    {identifiers.predicates.inhibition : {"S": [(arac,identifiers.objects.inhibitor)], 
                                          "O" : [(pbad,identifiers.objects.inhibited)]}},

    {identifiers.predicates.stimulation : {"S": [(iptg_laci,identifiers.objects.stimulator)], 
                                           "O" : [(plac,identifiers.objects.stimulated)]}},

    {identifiers.predicates.stimulation : {"S": [(atc_tetr,identifiers.objects.stimulator)], 
                                           "O" : [(ptetr,identifiers.objects.stimulated)]}},

    {identifiers.predicates.stimulation : {"S": [(ara_arac,identifiers.objects.stimulator)], 
                                           "O" : [(pbad,identifiers.objects.stimulated)]}},

    {identifiers.predicates.stimulation : {"S": [(hsl_luxr,identifiers.objects.stimulator)],
                                           "O" : [(pluxstar,identifiers.objects.stimulated)]}},

    {identifiers.predicates.stimulation : {"S": [(lasahl_lasr,identifiers.objects.stimulator)],
                                           "O" : [(plas,identifiers.objects.stimulated)]}},

    {identifiers.predicates.stimulation : {"S": [(hsl_luxr,identifiers.objects.stimulator)],
                                           "O" : [(plux,identifiers.objects.stimulated)]}},

    {identifiers.predicates.noncovalent_bonding : {"S": [(ara,identifiers.objects.reactant),(arac,identifiers.objects.reactant)],
                                                   "O" : [(ara_arac,identifiers.objects.product)]}},

    {identifiers.predicates.noncovalent_bonding : {"S": [(atc,identifiers.objects.reactant),(tetr,identifiers.objects.reactant)],
                                                   "O" : [(atc_tetr,identifiers.objects.product)]}},

    {identifiers.predicates.noncovalent_bonding : {"S": [(iptg,identifiers.objects.reactant),(laci,identifiers.objects.reactant)],
                                                   "O" : [(iptg_laci,identifiers.objects.product)]}},

    {identifiers.predicates.noncovalent_bonding : {"S": [(hsl,identifiers.objects.reactant),(luxr,identifiers.objects.reactant)],
                                                   "O" : [(hsl_luxr,identifiers.objects.product)]}},

    {identifiers.predicates.noncovalent_bonding : {"S": [(rhlahl,identifiers.objects.reactant),(rhlr,identifiers.objects.reactant)],
                                                   "O" : [(rhlahl_rhlr,identifiers.objects.product)]}},
    {identifiers.predicates.noncovalent_bonding : {"S": [(lasahl,identifiers.objects.reactant),(lasr,identifiers.objects.reactant)],
                                                   "O" : [(lasahl_lasr,identifiers.objects.product)]}}]


object_aliases = {
    identifiers.objects.DNA :                 {"nucleic acid",
                                               "deoxyribonucleic",
                                               "deoxyribonucleic acid",
                                               "polynucleotide chains",
                                               "polynucleotides"},
    identifiers.objects.DNARegion :           {"nucleic acid",
                                               "deoxyribonucleic",
                                               "deoxyribonucleic acid",
                                               "polynucleotide chains",
                                               "polynucleotides"},
    identifiers.objects.RNA :                 {"ribonucleic acid",
                                               "ribonucleic",
                                               "single-stranded molecule"},
    identifiers.objects.RNARegion :           {"ribonucleic acid",
                                               "ribonucleic",
                                               "single-stranded molecule"},
    identifiers.objects.protein :             {"amino",
                                               "amino acid"},
    identifiers.objects.smallMolecule :       {"glucose"},
    identifiers.objects.complex :             {"group"},
    identifiers.objects.promoter :            {"regulatory",
                                               "initiation",
                                               "control"},
    identifiers.objects.rbs :                 {"ribosome",
                                               "binding site",
                                               "shine–dalgarno",
                                               "ribosome entry site"},
    identifiers.objects.cds :                 {"CDS",
                                               "coding region",
                                               "codes",
                                               "coding",
                                               "contiguous"},
    identifiers.objects.terminator :          {"end",
                                               "terminate transcription",
                                               "gene end",
                                               "transcriptional termination"},
    identifiers.objects.engineeredRegion :    {"construct",
                                               "engineered sequence",
                                               "engineered"},
    identifiers.objects.engineeredGene :      {"engineered gene",
                                               "engineered fusion gene"},
    identifiers.objects.gene :                {"functional transcript",
                                               "region"},
    identifiers.objects.mRNA :                {"messenger",
                                               "intermediate molecule",
                                               "template RNA",
                                               "informational RNA"},
    identifiers.objects.sgRNA :               {"guide",
                                               "small guide",
                                               "small guide RNA"},
    identifiers.objects.transcriptionFactor : {"dna binding transcription factor activity"},
    identifiers.objects.effector :            {"activity modifier",
                                               "modulator"},
    identifiers.objects.operator :            {"operator segment"},
    identifiers.objects.engineeredTag :       {"engineered tag"},
    identifiers.objects.tag :                 {"identification",
                                               "tag"},
    identifiers.objects.startCodon :          {"initiation",
                                               "first codon"},
    identifiers.objects.nonCovBindingSite :   {"binding Site",
                                               "non-covalent",
                                               "non covalent"},
}

interaction_aliases = {
    (identifiers.objects.inhibitor,identifiers.objects.inhibition,identifiers.objects.inhibited) : ["repress","inhibit","prohibit","prevent","suppress","negative modulat"],
    (identifiers.objects.stimulator,identifiers.objects.stimulation,identifiers.objects.stimulated) : ["activat","stimulat","galvanis","galvaniz"],
    (identifiers.objects.modifier,identifiers.objects.biochemical_reaction,identifiers.objects.modified) : ["modifi","ionis","ioniz","chang","modifi"],
    (identifiers.objects.reactant,identifiers.objects.biochemical_reaction,identifiers.objects.product) : ["modifi","ionis","ioniz","react","consum","produc"],
    (identifiers.objects.reactant,identifiers.objects.noncovalent_bonding,identifiers.objects.product) : ["bond","format","fasten","react","consum","produc"],    
    (identifiers.objects.reactant,identifiers.objects.degradation,None) : ["degrad","deterior","declin","react","consum"],
    (identifiers.objects.template,identifiers.objects.genetic_production,identifiers.objects.template) : ["composite biochemical process","gene convers"],
    (identifiers.objects.modifier,identifiers.objects.control,identifiers.objects.modified) : ["modul","regul","control","modifi","chang"]}

    
identifier_map = {
        identifiers.objects.inhibition               : identifiers.predicates.inhibition,
        identifiers.objects.stimulation              : identifiers.predicates.stimulation,
        identifiers.objects.biochemical_reaction     : identifiers.predicates.biochemical_reaction,
        identifiers.objects.noncovalent_bonding      : identifiers.predicates.noncovalent_bonding,
        identifiers.objects.degradation              : identifiers.predicates.degradation,
        identifiers.objects.genetic_production       : identifiers.predicates.genetic_production,
        identifiers.objects.control                  : identifiers.predicates.control,
}

interaction_tag_list = [ 
    ((identifiers.objects.inhibitor,identifiers.objects.gp_promoter),(identifiers.objects.inhibition),(identifiers.objects.inhibited)),
    ((identifiers.objects.stimulator,identifiers.objects.gp_promoter),(identifiers.objects.stimulation),(identifiers.objects.stimulated)),
    ((identifiers.objects.modifier,identifiers.objects.reactant),(identifiers.objects.biochemical_reaction),(identifiers.objects.modified,identifiers.objects.product)),
    ((identifiers.objects.modifier),(identifiers.objects.control),(identifiers.objects.modified)),
    ((identifiers.objects.reactant),(identifiers.objects.degradation),None),
    ((identifiers.objects.reactant),(identifiers.objects.noncovalent_bonding),(identifiers.objects.product)),
    ((identifiers.objects.template,identifiers.objects.gp_promoter),(identifiers.objects.genetic_production),(identifiers.objects.product))
]

import re
def _get_name(subject):
    split_subject = _split(subject)
    if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
        return split_subject[-2]
    else:
        return split_subject[-1]

def _split(uri):
    return re.split('#|\/|:', uri)
    
