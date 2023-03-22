from rdflib import URIRef,Literal
import re
from app.enhancer.data_miner.ontology.ontology_term_map import OntologyTermMap,Identifiers
from app.enhancer.data_miner.ontology.server_interface.server import OntologyInterface

select_threshold = 20
object_threshold = 5

class OntologyMediator:
    def __init__(self):
        self.ontology_interface = OntologyInterface()
        self.language_mapper = OntologyTermMap(self.ontology_interface)
    
    def search(self,pattern):
        '''
        An input pattern likely will not actually pertain to a triple in the ontology.
        An identifier may:
            1. Be masked by another uri (http://identifiers.org/biomodels.sbo/SBO:0000645 -> http://biomodels.net/SBO/SBO_0000251)
            2. The ontologys identifier is formatted differently to the input.
            3. The input identifier is a id make specifically for this tool and needs to be resolved. (The handler giving a proprietary identifier)
        Certain Input identifiers may map to more than one ontology identifier.
        A resolution step occurs where all uris in the pattern are unmasked/resolved.
        '''
        res = []
        subj,pred,obj = pattern
        subjects = self._resolve_subject(subj)
        for s,ontology_code in subjects:
            predicates = self._resolve_predicate(pred,ontology_code)
            len_p = len(predicates) if predicates is not None else 1
            if len_p == 0:
                continue
            objects = self._resolve_object(obj)
            len_o = len(objects) if objects is not None else 1
            if len_p * len_o > select_threshold or len_o >= object_threshold:
                # Some queries produce huge sparql queries which make
                # the server throw errors. Instead chunk the query.
                res = res + self._federate_query(s,predicates,objects,ontology_code,pred)
            else:
                n_pattern = (s,predicates,objects)
                result =  self.ontology_interface.select(n_pattern,ontology_code=ontology_code)
                res = res + self._normalise_results(result,pred) 
        return res

    def unmask_uri(self,uri):
        resolved_uri = self._resolve_subject(uri)
        if len(resolved_uri) == 0:
            return None
        if len(resolved_uri[0]) == 0:
            return None
        return resolved_uri[0][0] 

    def mask_uri(self,uri):
        ontology_codes = self.ontology_interface.get_ontology_codes(subject=uri)
        if len(ontology_codes) == 0:
            return None
        if len(ontology_codes) > 1:
            raise Exception(f"WARN:: {uri} produces more than one query code.")
        ontology_code = ontology_codes[0]
        mask_namespace = self.ontology_interface.get_standard_mask(ontology_code=ontology_code)
        if len(mask_namespace) == 0:
            # Need to find a way to find a standard mask if not present (Never should have a server 
            # graph in the onto graph without one so should never occur.)
            raise NotImplementedError()
        mask_namespace = mask_namespace[0]
        query_code = self._mask_query_code(uri,ontology_code)
        masked_uri = self._rebuild(mask_namespace,query_code,uri)
        return masked_uri

    def _resolve_subject(self,s):
        if s is not None:
            subjects = []
            ontology_codes = self.ontology_interface.get_ontology_codes(subject=s)
            for ontology_code in ontology_codes:
                namespaces = self.ontology_interface.get_namespaces(ontology_code=ontology_code)
                for namespace in namespaces:
                    code = self._unmask_query_code(s,ontology_code)
                    subject = self._rebuild(namespace,code,s)
                    subjects.append((subject,ontology_code))
        else:
            subjects = [(None,q_c) for q_c in self.ontology_interface.get_ontology_codes()]
        return subjects

    def _resolve_predicate(self,predicates,ontology_code):
        if not isinstance(predicates,(set,list,tuple)):
            predicates = [predicates]
        ids = []
        for p in predicates:
            subject = URIRef(Identifiers.namespace.value + ontology_code)
            ids = ids + [o[2] for o in self.language_mapper.search((subject,p,None))]
        return ids

    def _resolve_object(self,o):
        if o is None:
            objects = [None]
        elif isinstance(o,(list,set,tuple)):
            objects = o
        else:
            objects = [o]
        return objects
       
    def _unmask_query_code(self,identifier,ontology_code):
        # Nuances of different ontologies there are patterns 
        # but only within subsets of ontologies.
        code = re.split(r'#|\/', str(identifier))[-1]
        ontology_code = ontology_code.lower()
        code_u_present = code.lower().count(f'{ontology_code}:') > 0
        code = code.replace(ontology_code + ":", "")
        if code_u_present:
            code = code.replace(":","_")
        return code

    def _mask_query_code(self,identifier,ontology_code):
        # Nuances of different ontologies there are patterns 
        # but only within subsets of ontologies.
        code = re.split(r'#|\/', str(identifier))[-1]
        ontology_code = ontology_code.lower()
        code_u_present = code.lower().count(f'{ontology_code}_') > 0
        code = code.replace(ontology_code + ":","")
        if code_u_present:
            code = code.replace("_",":")            
        return code

    def _federate_query(self,subject,predicates,objects,ontology_code,o_pred):   
        def does_intersect(s,p,result):
            does_intersect_triples = []
            for s1,p1,o1 in result:
                if s == s1 and p == p1:
                    does_intersect_triples.append((s1,p1,o1))
            if does_intersect_triples == []:
                return False,does_intersect_triples
            return True,does_intersect_triples

        def intersect(results):
            final_results = []
            for s,p,o in results[0]: 
                staged_triples = []
                for result in results[1:]:
                    _does_intersect,triples = does_intersect(s,p,result)
                    if not _does_intersect:
                        break
                    else:
                        staged_triples = staged_triples + triples
                else:
                    final_results.append((s,p,o))
                    final_results = final_results + staged_triples
            return final_results

        results = []
        for o in objects:
            n_pattern = (subject,predicates,o)
            result =  self.ontology_interface.select(n_pattern,ontology_code=ontology_code)
            n_res = self._normalise_results(result,o_pred)
            results.append(n_res)

        if len(results) == 1:
            results = results[0]
        elif len(results) > 1:
            results = intersect(results)
        return list(set(results))

    def _rebuild(self,new_ns,new_code,old_identifier):
        old_code = self._get_code(old_identifier)
        token = old_identifier[-(len(old_code) + 1)]
        if token == ":":
            token = "/"
        final_identifier = URIRef(new_ns + token + new_code)
        return final_identifier

    def _normalise_results(self,results,original_predicate):
        def _prune_literal(literal):
            prune_regex = ["INSDC.*:"]
            for pr in prune_regex:
                literal = re.sub(pr, '', literal)
            return Literal(literal.lower())

        normalised_results = []
        for s,p,o in results:
            try:
                s = self.mask_uri(s)
            except ValueError:
                # Some graphs produce duplicates with nodeids.
                continue
            
            if original_predicate is not None:
                p = original_predicate
            o = _prune_literal(o)
            normalised_results.append((s,p,o))            
        return normalised_results

    def _get_code(self,identifier):
        split = self._split(str(identifier))
        if len(split) == 0:
            raise ValueError(f'{identifier} doesnt have a code')
        return split[-1]
    
    def _split(self,uri):
        return re.split(r'#|\/|:', str(uri))