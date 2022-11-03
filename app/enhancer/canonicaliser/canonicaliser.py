'''
Case Group 1: A direct reference to a standard part is in the uri. 
    Case 1.1: The name is a standard name but part of a fake uri:
    Case 1.2. The name has an indirect reference,
Case Group 2: The object has a sequence match with a standardised part.
    Case 2.1: Direct Sequence Match
    Case 2.2: Similar Sequence Match
Case Group 3: Metadata reveals a standardised part.
    Case 3.1: A direct reference is encoded.
    Case 3.2. A name is driectrly encoded.
    Case 3.3: Metadata query reveals a potential reference
Case Group 4: The object is the parent/child of 
                in some way refers to a known standardised part. 
                
'''

'''
Overview of the process:
1. Absolute References
    1.1. Check if an entity name refers directly to a record.
    1.2. Check if the Truth Graph contains a high confidence synonym.
    1.3. Check for a full sequence match.
    1.4. Check metadata for a direct record.
2. Potential References
    2.1. Partial Sequence Match.
    2.1  Mid/Low confidence synonym from Truth Graph.
    2.1. Partial Descriptor From metadata.

3. Post-Processing Score
    3.1. Chance to increase score by comparing entites within the graph.
    
'''
import uuid
from app.converter.sbol_convert import convert

class Canonicaliser:
    def __init__(self,graph,miner):
        self._wg = graph
        self._tg = graph.truth
        self._miner = miner

    def design(self,graph_name,mode="automated"):
        dg = self._wg.get_design(graph_name)
        replacements = {}
        feedback = {}
        for entity in dg.get_physicalentity():
            if not self._miner.is_reference(entity.get_key()):
                key = entity.get_key()
                subject = self.get_absolute_references(entity)
                if subject is not None:
                    replacements[key] = {subject : 1.0}
                    if mode == "automated":    
                        self.apply({key:subject},graph_name)
                    continue 
                if mode != "automated":
                    p_subjects,fback = self.get_potential_references(entity)
                    if len(p_subjects) > 0:
                        replacements[key] = p_subjects
                        feedback.update(fback)
        for r,subs in replacements.items():
            replacements[r] = self._post_rank(r,subs,dg)

        return replacements,feedback

    def entity(self,entity,graph_name,mode="automated"):
        dg = self._wg.get_design(graph_name)
        subjects = {}
        if self._miner.is_reference(entity.get_key()):
            return {},{}
        # Absolute doesnt provide feedback (in theory they should be definitive).
        subject = self.get_absolute_references(entity)
        if subject is not None:
            if mode == "automated":    
                self.apply({entity.get_key():subject},graph_name)
            return {subject:1.0},{}

        if mode != "automated":
            subjects,fback = self.get_potential_references(entity)
            if subjects != []:
                parent = dg.get_parents(entity)
                if len(parent) == 0:
                    parent = None
                else:
                    parent == parent[0]
                subjects = self._post_rank(entity,subjects,dg,parent=parent)
                return subjects,fback
        return subjects,{}

    def get_absolute_references(self,entity):
        name = entity.name
        record = self._miner.get_external(name)
        if record is not None:
            return self._miner.get_graph_subject(record,[name])
        res = self._tg.synonyms.get(synonym=name)
        if res != []:
            assert(len(res) == 1)
            if res[0].confidence == 100:
                return res[0].n
        if hasattr(entity,"hasSequence"):
            sequence = entity.hasSequence
            record = self._miner.full_sequence_match(sequence)
            if record is not None:
                return record
        if hasattr(entity,"description"):
            descriptions = entity.description
            return self._miner.mine_explicit_reference(descriptions)
        return None
        
    def get_potential_references(self,entity):
        name = entity.name
        e_type = entity.get_type()
        feedback = {}
        subjects = {}

        def _add_feedback(subj,conf,feedback_str):
            if subj in subjects:
                subjects[subj] = subjects[r] + conf / 2
                feedback[subj] += " - " + feedback_str
            else:
                subjects[subj] = conf
                feedback[subj] = feedback_str
        
        if hasattr(entity,"hasSequence"):
            sequence = entity.hasSequence
            # Partial Sequence Search
            for record,similarity in self._miner.partial_sequence_match(sequence).items():
                _add_feedback(record,similarity,"Partial Sequence Match")

        # Metadata
        queries = [name]
        # Pool Potential descriptors.
        if hasattr(entity,"description"):
            queries += self._miner.get_descriptors(entity.description)
        for query in queries:
            # Check if truth graph has it stored.
            res = self._tg.synonyms.get(synonym=query)
            if len(res) != 0:
                for r in res:
                    _add_feedback(r.n,r.confidence,query)
            else:
                # Try mine via external.
                records = list(self._miner.query_external(query,lazy=True))
                if len(records) != 0:
                    graphs = [self._miner.get_external(r) for r in records[0] if r not in subjects]
                    for leaf in self._miner.get_leaf_subjects(graphs,e_type,query):
                        _add_feedback(leaf,0,f'Using Query: {query}')
        return subjects,feedback


    def apply(self,replacements,graph_name):
        dg = self._wg.get_design(graph_name)
        for old,new in replacements.items():
            dg.replace_label(str(old),str(new))
        return replacements


    def _post_rank(self,entity,potentials,dg,parent=None):
        '''
        Rankings such as neighbourhood similarity may perform 
        better when other entities have been canonicalised.
        This methods implements these rankings.
        Rankings will only change with Automated and 
        on potential references.
        '''
        def _add_confidence(node,row):
            new_c = potentials[node] + row["similarity"]
            if new_c > 0:
                new_c = 1.0
            potentials[node] = new_c
        gn = str(uuid.uuid4())
        if parent is not None:
            fn = self._miner.get_external(parent)
            if fn is not None:
                convert(fn,self._wg.driver,gn)
        for p in potentials:
            fn = self._miner.get_external(p)
            convert(fn,self._wg.driver,gn)
        p_gn = str(uuid.uuid4())
        dg = self._wg.get_design(dg.name + [gn])
        tmp = dg.project.hierarchy(p_gn,direction="UNDIRECTED")
        res = dg.procedure.node_similarity(p_gn)
        seen_combos = []
        for r in res:
            n1 = r["node1"].get_key()
            n2 = r["node2"].get_key()
            if {n1,n2} in seen_combos:
                continue
            seen_combos.append({n1,n2})
            if n1 == entity and n2 in potentials:
                _add_confidence(n2,r)
            if n2 == entity and n1 in potentials:
                _add_confidence(n1,r)
        dg.project.drop(p_gn)
        self._wg.remove_design(gn)
        return potentials
        