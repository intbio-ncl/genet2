from app.utility.change_log.logger import logger

update_clauses = ["CREATE", "SET"]

class Operations:
    def __init__(self, graph_object, index, use_properties=True):
        self.graph_object = graph_object
        self.index = index
        self.ops = {self.create: None, self.match: None,
                    self.set: None, self.replace: None,
                    self.remove:None,self.remove_properties:None,
                    self.add_label:None, self.replace_label: None}
        self.use_properties = use_properties

    def enable_create(self):
        self.ops[self.create] = True

    def enable_match(self,use_id=False):
        self.ops[self.match] = [use_id]

    def enable_set(self, new_props):
        self.ops[self.set] = new_props

    def enable_replace_properties(self, new_props):
        self.ops[self.replace] = new_props

    def enable_remove(self):
        self.ops[self.remove] = True
    
    def enable_remove_properties(self, remove_props):
        self.ops[self.remove_properties] = remove_props

    def enable_add_label(self,label):
        self.ops[self.add_label] = label

    def enable_replace_label(self,old,new):
        self.ops[self.replace_label] = [old,new]

    def generate(self, code,log=True):
        qry_str = ""
        for k, v in self.ops.items():
            if v is  None:
                continue
            elif v is True:
                qry_str += k(log=log)
            elif isinstance(v,list):
                qry_str += k(*v,log=log)
            else:
                qry_str += k(v,log=log)
        if qry_str == "":
            return qry_str
        if not any(ext in qry_str for ext in update_clauses):
            qry_str += f' RETURN {code}{self.index}'
        return qry_str

    def set(self,new_props,code):
        set = "SET"
        n_id = f'{code}{self.index}'
        for c_index, (k, v) in enumerate(new_props.items()):
            if isinstance(v, list):
                if not hasattr(self.graph_object,k):
                    set += f' {n_id}.`{k}` =  {v},'
                else:
                    set += f' {n_id}.`{k}` =  {n_id}.`{k}` + {v},'
                set = set[:-1]
            else:
                set += f' {n_id}.`{k}` = "{v}"'
            if c_index < len(new_props) - 1:
                set += ",\n "
            else:
                set += "\n"
        set = set[:-1]
        return set

    def add_label(self,code,label):
        return f' SET {code}{self.index}:`{label}`'

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
                    if isinstance(ele,list):
                        set += f' {n_id}.`{k}` = [x IN {n_id}.`{k}` WHERE NOT x IN {ele}],'
                    else:
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

    def replace_label(self,old,new):
        pass

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

    def _where(self,use_id):
        where = ""
        labels = self.graph_object.get_labels()


        for c_index, i in enumerate(labels):
            where += f'n{self.index}:`{i}`'
            if c_index < len(labels) - 1:
                where += " AND "
        if use_id:
            if where != "":
                where += " AND "
            where += f" ID(n{self.index}) = {self.graph_object.id} "
        
        gn = self.graph_object.graph_name
        if len(where) > 0:
            where += " AND "
        where += f'ALL(a IN {gn} WHERE a IN n{self.index}.`graph_name`)'

            
        return where


class NodeOperations(Operations):
    def __init__(self, graph_object, index, use_properties=True):
        super().__init__(graph_object, index, use_properties)

    def generate(self,log=True):
        return super().generate("n",log=log)

    def create(self,log=True):
        qry = f'CREATE (n{self.index}:{self.list_to_query(self.graph_object.get_labels())} '
        qry += f'{{{self.get_properties()}}})'
        if log:
            logger.add_node(self.graph_object,self.graph_object.graph_name)
        return qry

    def match(self,use_id=False,log=True):
        return f"""MATCH (n{self.index} {{{self.get_properties(add_lists=False)}}}) WHERE {self._where(use_id)}"""

    def set(self, new_props,log=True):
        qry = super().set(new_props,"n")
        self.graph_object.update(new_props)
        if log:
            logger.replace_node_property(self.graph_object,
                new_props,self.graph_object.graph_name)
        return qry

    def replace(self, new_props,log=True):
        self.graph_object.replace(new_props)
        if log:
            logger.replace_node_property(self.graph_object,new_props,self.graph_object.graph_name)
        return super().replace(new_props,"n")

    def remove(self,log=True):
        if log:
            logger.remove_node(self.graph_object,self.graph_object.graph_name)
        return super().remove("n")

    def add_label(self,label,log=True):
        return super().add_label("n",label)

    def remove_properties(self,remove_props,log=True):
        qry = super().remove_properties(remove_props,"n")
        self.graph_object.remove(remove_props)
        return qry

    def replace_label(self, old, new,log=True):
        if log:
            logger.replace_node(old,new,self.graph_object.graph_name)
        return f'''REMOVE n{self.index}:`{old}`
                   SET n{self.index}:`{new}`'''
    

class EdgeOperations(Operations):
    def __init__(self, graph_object, index, n_index, v_index, use_properties=True):
        super().__init__(graph_object, index, use_properties)
        self.n_index = n_index
        self.v_index = v_index

    def generate(self,log=True):
        return super().generate("e",log=log)

    def create(self,log=True):
        qry = ""
        n_op = NodeOperations(self.graph_object.n, self.n_index)
        v_op = NodeOperations(self.graph_object.v, self.v_index)
        qry += n_op.match() + "\n"
        qry += v_op.match() + "\n"
        qry += "CREATE"
        qry += f'(n{self.n_index})'
        qry += f'-[r{self.index}:{"`"+self.graph_object.get_type()+"`"} {{{self.get_properties()}}}]->'
        qry += f'(n{self.v_index})'
        if log:
            logger.add_edge(self.graph_object,self.graph_object.graph_name)
        return qry

    def match(self,use_id,log=True):
        e = f': `{self.graph_object.get_type()}`'
        n_op = NodeOperations(self.graph_object.n, self.n_index)
        v_op = NodeOperations(self.graph_object.v, self.v_index)
        n_where = n_op._where(use_id)
        v_where = v_op._where(use_id)
        n = f'(n{self.n_index} {{{self.get_properties(self.graph_object.n,add_lists=False)}}})'
        e = f'[e{self.index}{e} {{{self.get_properties(add_lists=False)}}}]'
        v = f'(n{self.v_index} {{{self.get_properties(self.graph_object.v,add_lists=False)}}})'
        return f"""MATCH {n}-{e}->{v} \n WHERE {n_where} AND \n {v_where} \n"""

    def set(self, new_props,log=True):
        self.graph_object.update(new_props)
        if log:
            logger.replace_edge_property(self.graph_object,
                new_props,self.graph_object.graph_name)
        return super().set(new_props,"e")

    def replace(self, new_props,log=True):
        self.graph_object.replace(new_props)
        if log:
            logger.replace_edge_property(self.graph_object,
                new_props,self.graph_object.graph_name)
        return super().replace(new_props,"e")

    def remove(self,log=True):
        if log:
            logger.remove_edge(self.graph_object,self.graph_object.graph_name)
        return super().remove("e")

    def add_label(self,label,log=True):
        return super().add_label("e",label)

    def remove_properties(self,remove_props,log=True):
        qry = super().remove_properties(remove_props,"e")
        self.graph_object.remove(remove_props)
        return qry

    def replace_label(self, old, new,log=True):
        if log:
            logger.replace_edge(old,new,self.graph_object.graph_name)
        return f'''REMOVE e{self.index}:`{old}`
                   SET e{self.index}:`{new}`'''