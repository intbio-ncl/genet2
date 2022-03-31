update_clauses = ["CREATE", "SET"]


class Operations:
    def __init__(self, graph_object, index, use_properties=True):
        self.graph_object = graph_object
        self.index = index
        self.ops = {self.create: False, self.match: False,
                    self.set: False, self.replace: False,
                    self.remove:False,self.remove_properties:False}
        self.use_properties = use_properties

    def enable_create(self):
        self.ops[self.create] = True

    def enable_match(self):
        self.ops[self.match] = True

    def enable_set(self, new_props):
        self.ops[self.set] = new_props

    def enable_replace_properties(self, new_props):
        self.ops[self.replace] = new_props

    def enable_remove(self):
        self.ops[self.remove] = True
    
    def enable_remove_properties(self, remove_props):
        self.ops[self.remove_properties] = remove_props

    def generate(self, code):
        qry_str = ""
        for k, v in self.ops.items():
            if isinstance(v, bool):
                if v == True:
                    qry_str += k()
            else:
                qry_str += k(v)

        if not any(ext in qry_str for ext in update_clauses):
            qry_str += f' RETURN {code}{self.index}'
        return qry_str

    def set(self,new_props,code):
        set = "SET"
        n_id = f'{code}{self.index}'
        for c_index, (k, v) in enumerate(new_props.items()):
            if isinstance(v, list):
                for ele in v:
                    set += f' {n_id}.`{k}` =  {n_id}.`{k}` + "{ele}",'
                set = set[:-1]
            else:
                set += f' {n_id}.`{k}` = "{v}"'
            if c_index < len(new_props) - 1:
                set += ",\n "
            else:
                set += "\n"
        set = set[:-1]
        return set

    def replace(self, new_props,code):
        return f'SET {code}{self.index} = {{{ self.dict_to_query(new_props)}}} \n'

    def remove(self,code):
        return f'DETACH DELETE {code}{self.index}'
    
    def remove_properties(self,remove_props,code):
        set = "SET"
        n_id = f'{code}{self.index}'
        for c_index, (k, v) in enumerate(remove_props.items()):
            if isinstance(v, list):
                for ele in v:
                    set += f' {n_id}.`{k}` = [x IN {n_id}.`{k}` WHERE x <> "{ele}"],'
                set = set[:-1]
            else:
                set += f' {n_id}.`{k}` = {{}}'
            if c_index < len(remove_props) - 1:
                set += ",\n "
            else:
                set += "\n"
        set = set[:-1]
        return set

    def get_properties(self,graph_object = None,add_lists=True):
        if self.use_properties:
            if graph_object is not None:
                return self.dict_to_query(graph_object.get_properties(),add_lists)
            return self.dict_to_query(self.graph_object.get_properties(),add_lists)
        return ""
        
    def dict_to_query(self, items,add_lists=True):
        f_str = ""
        if not add_lists:
            items = {k:v for k,v in items.items() if not isinstance(v,(set,list,tuple))}.items()
        else:
            items = items.items()

        for index, (k, v) in enumerate(items):
            v = v if isinstance(v, list) else f'"{v}"'
            f_str += f'`{k}`: {v}'
            if index != len(items) - 1:
                f_str += ","
        return f_str

    def list_to_query(self, items):
        f_str = ""
        for index, item in enumerate(items):
            f_str += f'`{item}`'
            if index < len(items) - 1:
                f_str += ":"
        return f_str

    def _where(self):
        where = ""
        labels = self.graph_object.get_labels()
        for c_index, i in enumerate(labels):
            where += f'n{self.index}:`{i}`'
            if c_index < len(labels) - 1:
                where += " AND "

        props = self.graph_object.get_properties()
        for index,(k,v) in enumerate({k:v for k,v in props.items() if isinstance(v,(set,list,tuple))}.items()):
            if where == "":
                where = "WHERE "
            elif index < len(props) - 1 or index == 0:
                where += " AND "

            where += f'ALL(a IN {v} WHERE a IN n{self.index}.`{k}`)'
        return where


class NodeOperations(Operations):
    def __init__(self, graph_object, index, use_properties=True):
        super().__init__(graph_object, index, use_properties)

    def generate(self):
        return super().generate("n")

    def create(self):
        qry = f'CREATE (n{self.index}:{self.list_to_query(self.graph_object.get_labels())} '
        qry += f'{{{self.get_properties()}}})'
        return qry

    def match(self):
        return f"""MATCH (n{self.index} {{{self.get_properties(add_lists=False)}}}) WHERE {self._where()}"""

    def set(self, new_props):
        qry = super().set(new_props,"n")
        self.graph_object.update(new_props)
        return qry

    def replace(self, new_props):
        self.graph_object.replace(new_props)
        return super().replace(new_props,"n")

    def remove(self):
        return super().remove("n")

    def remove_properties(self,remove_props):
        qry = super().remove_properties(remove_props,"n")
        self.graph_object.remove(remove_props)
        return qry

    

class EdgeOperations(Operations):
    def __init__(self, graph_object, index, n_index, v_index, use_properties=True):
        super().__init__(graph_object, index, use_properties)
        self.n_index = n_index
        self.v_index = v_index

    def generate(self):
        return super().generate("e")

    def create(self):
        qry = ""
        n_op = NodeOperations(self.graph_object.n, self.n_index)
        v_op = NodeOperations(self.graph_object.v, self.v_index)
        qry += n_op.match() + "\n"
        qry += v_op.match() + "\n"
        qry += "CREATE"
        qry += f'(n{self.n_index})'
        qry += f'-[r{self.index}:{self.list_to_query(self.graph_object.get_labels())} {{{self.get_properties()}}}]->'
        qry += f'(n{self.v_index})'
        return qry

    def match(self):
        e = ":" + "" + \
            "|".join(["`" + e + "`" for e in self.graph_object.get_labels()])

        n_op = NodeOperations(self.graph_object.n, self.n_index)
        v_op = NodeOperations(self.graph_object.v, self.v_index)
        n_where = n_op._where()
        v_where = v_op._where()
        n = f'(n{self.n_index} {{{self.get_properties(self.graph_object.n,add_lists=False)}}})'
        e = f'[e{self.index}{e} {{{self.get_properties(add_lists=False)}}}]'
        v = f'(n{self.v_index} {{{self.get_properties(self.graph_object.v,add_lists=False)}}})'
        return f"""MATCH {n}-{e}->{v} \n WHERE {n_where} AND \n {v_where} \n"""

    def set(self, new_props):
        self.graph_object.update(new_props)
        return super().set(new_props,"e")

    def replace(self, new_props):
        self.graph_object.replace(new_props)
        return super().replace(new_props,"e")

    def remove(self):
        return super().remove("n")

    def remove_properties(self,remove_props):
        qry = super().remove_properties(remove_props,"e")
        self.graph_object.remove(remove_props)
        return qry