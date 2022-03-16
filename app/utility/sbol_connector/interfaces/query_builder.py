class QueryBuilder:
    def __init__(self):
        self.metadata_predicates = {"title" : "dcterms",
                                    "description" : "dcterms",
                                    "mutableNotes" : "sbh",
                                    "mutableDescription" : "sbh",
                                    "mutableProvenance" : "sbh"}

        self.prefixes = ("PREFIX sbol2: <http://sbols.org/v2#>\n" + 
                        "PREFIX dcterms: <http://purl.org/dc/terms/>\n" +
                        "PREFIX sbh: <http://wiki.synbiohub.org/wiki/Terms/synbiohub#>\n"+
                        "PREFIX igem: <http://wiki.synbiohub.org/wiki/Terms/igem#>\n"+
                        "PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\n"+
                        "PREFIX dc: <http://purl.org/dc/elements/1.1/>\n"+
                        "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n"+
                        "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n")

    
    def query(self,qry_string,limit=5):
        spql_string = f'{self.prefixes}\nSELECT DISTINCT ?subject\n'        
        spql_string = f'{spql_string}{self._where_meta_search(qry_string)}'
        spql_string = f'{spql_string} LIMIT {str(limit)}'
        return spql_string


    def count(self,qry_string):
        spql_string = f'{self.prefixes}\nSELECT (sum(?tempcount) as ?count) \nWHERE {{{{'
        spql_string = f'{spql_string}\n   SELECT (count(distinct ?subject) as ?tempcount)\n'
        spql_string = f'{spql_string}{self._where_meta_search(qry_string,1)}'
        spql_string = f'{spql_string}\n}}}}'
        return spql_string

    def _where_meta_search(self,qry_string,indent_level=0):
        indent = "   " * indent_level
        next_indent_level = indent_level+1
        parts = qry_string.split(" ")
        if len(parts) == 0:
            raise ValueError(f"Invalid Input QRY: {qry_string}")
        
        where_string = f'{indent}WHERE {self._contains_filter(parts,next_indent_level)}'
        where_string = f'{where_string}{self._top_level(next_indent_level)}'
        where_string = f'{where_string}{self._meta_optional(next_indent_level)}'
        where_string = f'{where_string}{indent}}}'
        return where_string


    def _contains_filter(self,parts,indent_level = 2):
        indent = "   " * indent_level
        next_indent_level = indent_level + 1
        filter_string = f'{{\n{indent}FILTER ('
        for index,p in enumerate(parts):
            contain_grp = self._contains_group(p,next_indent_level)
            if index < len(parts) - 1:
                filter_string = f'{filter_string}({contain_grp})\n{indent}&&'
            else:
                filter_string = f'{filter_string}({contain_grp})'
        filter_string = f'{filter_string})'
        return filter_string

    def _contains_group(self,item,indent_level=2):
        indent = "   " * indent_level
        contain_grp = ""
        for p_index,predicate in enumerate(self.metadata_predicates.keys()):
            contain_grp = f"{contain_grp}\n{indent}CONTAINS(lcase(?{predicate}), lcase('{item}'))"
            if p_index < len(self.metadata_predicates) - 1:
                contain_grp = f'{contain_grp} ||'
        return contain_grp

    def _top_level(self,indent_level=1):
        indent = "   " * indent_level
        return f'\n{indent}?subject sbh:topLevel ?subject .\n'

    def _meta_optional(self,indent_level=1):
        meta_str = ""
        indent = "   " * indent_level
        for predicate,ns in self.metadata_predicates.items():
            meta_str = f'{meta_str}{indent}OPTIONAL {{ ?subject {ns}:{predicate} ?{predicate} .}}\n'
        return meta_str