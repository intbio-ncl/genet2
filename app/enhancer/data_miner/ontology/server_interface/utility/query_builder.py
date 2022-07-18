import re

from rdflib import URIRef,Literal

class QueryBuilder:
    def __init__(self):
        self.indent = "    "
        self._prefixes = {}
        self._prefix_map = {}
        self._name_store = []
        self._triple_store = []
    
    def select(self,pattern,namespace,limit=None):
        pattern = self._prefix_pattern(pattern)
        PREFIXES = self._build_prefixes()
        FROM = f'FROM <{namespace}>'
        WHERE = self._build_where(pattern)
        SELECT = self._build_select()

        spql_qry = f'{PREFIXES}\n{SELECT}\n{FROM}\n{WHERE}'
        if limit is not None:
            spql_qry = f'{spql_qry} LIMIT {str(limit)}'
        query = Query(spql_qry,self._triple_store)
        self._reset_data()
        return query

    def get_graphs(self):
        return Query("SELECT DISTINCT ?g WHERE { GRAPH ?g {?s a ?t}}",[(None,None,None)])

    def get_partial_predicates(self,partial_predicate,namespace):
        SELECT = f'SELECT DISTINCT ?p'
        FROM = f'FROM <{namespace}>'
        WHERE = f'WHERE {{ ?s ?p ?o . FILTER ({self.contains_filter("p",partial_predicate)})}}'
        qry_string = f'{SELECT}\n{FROM}\n{WHERE}'
        triple = [(None,Literal("?p"),None)]
        return Query(qry_string,triple)

    def contains_filter(self,identifier_pos,string):
        return f"CONTAINS(lcase(str(?{identifier_pos})),lcase('{string}'))"

    def lowercase_equals_filter(self,identifier_pos,string):
        return f'(lcase(str(?{identifier_pos})) = "{string}")'

    def _build_prefixes(self):
        PREFIXES = ""
        for name,prefix in self._prefixes.items():
            PREFIXES = f'{PREFIXES}PREFIX {name}: <{prefix}>\n'
        return PREFIXES

    def _build_select(self):
        SELECT = f'SELECT DISTINCT '
        names = list(set(self._name_store))
        for name in names:
            SELECT = f'{SELECT} ?{name}'
        return SELECT

    def _build_where(self,pattern):
        WHERE = "WHERE\n{"
        subjects,predicates,objects = pattern
        for subj in subjects:
            WHERE = f'{WHERE}\n{self.indent}{{'
            WHERE = f'{WHERE}{self._build_subject_where(subj,objects,predicates)}'
            WHERE = f'{WHERE}\n{self.indent}}}'
        WHERE = f'{WHERE}\n}}'
        return WHERE

    def _build_subject_where(self,subj,objs,preds):
        S_WHERE = "\n"
        for obj in objs:
            S_WHERE = f'{S_WHERE}{self._build_object_where(subj,obj,preds)}'
            S_WHERE = f'{S_WHERE}\n{self.indent}'
        
        S_WHERE = f'{S_WHERE}\n'
        return S_WHERE

    def _build_object_where(self,subj,obj,preds):
        O_WHERE = f'\n{self.indent*2}{{'
        for index,pred in enumerate(preds):
            if index != 0:
                O_WHERE = f'{O_WHERE}{self.indent*3}UNION {self._build_predicate_where(subj,obj,pred)}\n'
            else:
                O_WHERE = f'{O_WHERE}\n{self.indent*4}{self._build_predicate_where(subj,obj,pred)}\n'
        
        O_WHERE = f'{O_WHERE}\n{self.indent*2}}}'
        return O_WHERE

    def _build_predicate_where(self,subj,obj,pred):
        P_WHERE = f'{{'
        if subj is None:
            P_WHERE = f'{P_WHERE} ?subject'
            self._name_store.append("subject")
        else:
            prefix_name = self._prefix_map[subj]
            P_WHERE = f'{P_WHERE} {prefix_name}:{subj}'

        if pred is None:
            P_WHERE = f'{P_WHERE} ?predicate'
            self._name_store.append("predicate")
        else:
            prefix_name = self._prefix_map[pred]
            P_WHERE = f'{P_WHERE} {prefix_name}:{pred}'
        
        obj_var = self._build_var_name(obj,pred)
        P_WHERE = f'{P_WHERE} ?{obj_var} . '
        if obj is not None:
            P_WHERE = f'{P_WHERE} FILTER ({self.contains_filter(obj_var,obj)})'

        self._name_store.append(obj_var)
        s = self._rebuild_element(subj,"?subject")
        p = self._rebuild_element(pred,"?predicate")
        o = Literal(f'?{obj_var}')
        self._triple_store.append((s,p,o))

        P_WHERE = f'{P_WHERE}}}'
        return P_WHERE

    def _prefix_pattern(self,pattern):
        prefixes = {}
        prefix_map = {}
        def _handle_element(element):
            n_elements = []
            if isinstance(element,(list,set,tuple)):
                for e in element:
                    n_elements = n_elements + _handle_element(e)
            elif isinstance(element,URIRef):
                parts = self._split(element)
                name = parts[-2]
                n_element = parts[-1]
                prefix = element[0:-len(n_element)]
                prefixes[name] = prefix
                prefix_map[n_element] = name
                n_elements.append(n_element)
            else:
                n_elements.append(element)
            return n_elements

        subjects,predicates,objects = pattern
        n_subjects = _handle_element(subjects)
        n_predicates = _handle_element(predicates)
        n_objects = _handle_element(objects)
        new_pattern = (n_subjects,n_predicates,n_objects)
        self._prefixes = prefixes
        self._prefix_map = prefix_map
        return new_pattern

    def _split(self,uri):
        return re.split('#|\/|:', str(uri))

    def _build_var_name(self,*args):
        name = ("_".join([n.replace(" ","_")
                           .replace("-","_")
                           .lower() for n in args if n is not None]))
        if name == "":
            name = "object"
        return name

    def _rebuild_element(self,element,default):
        if element is None:
            return Literal(default)
        try:
            return URIRef(self._prefixes[self._prefix_map[element]] + element)
        except KeyError:
            return Literal(default)

    def _reset_data(self):
        self._prefixes = {}
        self._prefix_map = {}
        self._name_store = []
        self._triple_store = []

class Query:
    def __init__(self,query_string,triples):
        self.query_string = query_string
        self.triples = triples

    def __str__(self):
        return self.query_string

    def __repr__(self):
        return self.query_string