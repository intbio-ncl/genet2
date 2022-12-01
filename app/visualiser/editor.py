import re
from inspect import signature, getargspec
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from dash import callback_context

from app.visualiser.abstract_dashboard.utility.callback_structs import *
from app.visualiser.visual.editor import EditorVisual
from app.visualiser.abstract_dashboard.abstract import AbstractDash
from app.graph.utility.graph_objects.node import Node
assets_ignore = '.*bootstrap.*'

class EditorDash(AbstractDash):
    def __init__(self, name, server, graph):
        super().__init__(EditorVisual(graph), name, server,
                         "/editor/", assets_ignore=assets_ignore)
        self._build_app()
        
    def _build_app(self):
        form_elements, identifiers, maps = self._create_form_elements(self.visualiser, id_prefix=id_prefix)
        load_editor_output = Output(identifiers["view"].component_id,"value")
        e_update_i.update(identifiers)
        gns = [{"label": c, "value": c} for c in self.visualiser.get_design_names()]
        lp =  [{"label": c, "value": c} for c in self.visualiser.get_load_predicates()]
        inp = (self.create_dropdown(load_editor_states["graph_names"].component_id, gns, multi=True,placeholder="Load Design") + 
               self.create_dropdown(load_editor_states["load_predicate"].component_id,lp,placeholder="Load Predicate") +
               self.create_line_break(10) + self.create_button(load_editor_input.component_id,"Load Graph"))


        editor = self._create_editor()
        mg = self.create_div("editor",editor)
        acc_elements = [("Load Design", inp), ("Modify Graph",mg)]
        load_accordion = self.create_accordion("proj_accordion", acc_elements)

        form_div = self.create_div(graph_type_o["id"].component_id, form_elements)
        options = self.create_sidebar(not_modifier_identifiers["sidebar_id"], "Options", form_div, className="col sidebar")
        figure = self.visualiser.empty_graph(graph_id)
        graph = self.create_div(e_update_o["graph_id"].component_id, [figure])
        graph = self.create_div(modify_graph_o["graph_container"].component_id, graph,className="col")
        legend = self.create_div(e_update_o["legend_id"].component_id,[], className="col sidebar")

        col_names = [{"id" : "entity", "name" : "Entity"},
                     {"id" : "confidence","name" : "Confidence"},
                     {"id" : "comment","name" : "Comment"}]
        an_tbl = self.create_complex_table(add_node_o["data"].component_id, col_names)
        an_modal = self.create_modal(add_node_o["id"].component_id,add_node_i["close_an"].component_id,"Export", an_tbl)

        elements = options + graph + legend + an_modal
        container = self.create_div("row-main", elements, className="row flex-nowrap no-gutters")
        self.app.layout = self.create_div("main", load_accordion+container, className="container-fluid")[0]
        # Bind the callbacks
        def update_inputs_inner(style):
            return self.update_inputs(style)

        def load_inner(click,gns,lp):
            return self.load(click,gns,lp)

        def add_node_inner(o_click,c_click,is_open,n_key,n_type,n_seq,n_desc):
            return self.add_node(o_click,c_click,is_open,n_key,n_type,n_seq,n_desc)

        def modify_graph_inner(n_select,e_click,n_data,n_type,n_seq,n_desc,e_subj,e_pred,e_obj):
            return self.modify_graph(n_select,e_click,n_data,n_type,n_seq,n_desc,e_subj,e_pred,e_obj)

        def select_node_inner(aes_c,aeo_c,predicate,elements,data,es_values,eo_values):
            return self.select_node(aes_c,aeo_c,predicate,elements,data,es_values,eo_values)

        def update_graph_inner(*args):
            return self.update_graph(args)

        self.add_callback(update_inputs_inner, [update_i_i], [update_i_o])
        self.add_callback(load_inner, [load_editor_input], load_editor_output,load_editor_states.values())
        
        self.add_callback(select_node_inner, select_node_i.values(), select_node_o.values(),select_node_s.values())
        self.add_callback(add_node_inner, add_node_i.values(), add_node_o.values(),add_node_s.values())
        self.add_callback(modify_graph_inner, modify_graph_i.values(), modify_graph_o.values(),modify_graph_s.values())
        self.add_callback(update_graph_inner, e_update_i.values(), e_update_o.values())
        self.build()

    def update_inputs(self,style):
        return [[{"label": c, "value": c} for c in self.visualiser.get_design_names()]]

    def load(self,click,gns,lp):
        if not gns or not isinstance(self.visualiser, EditorVisual):
            raise PreventUpdate()
        changed_id = [p['prop_id'] for p in callback_context.triggered][0]
        if load_editor_input.component_id in changed_id:
            self.visualiser.set_design_names(gns,lp)
            return [self.visualiser.set_full_graph_view.__name__]
        else:
            raise PreventUpdate()

    def update_graph(self, *args):
        if not isinstance(self.visualiser, EditorVisual):
            raise PreventUpdate()
        args = args[0]
        for index, setter_str in enumerate(args):
            if setter_str is not None:
                #try:
                setter = getattr(self.visualiser, setter_str, None)
                parameter = None
                #except TypeError:
                    # Must be a input element rather than a checkbox.
                    # With annonymous implementation this is tough.
                    #to_call = list(update_i.keys())[index]
                    #parameter = setter_str
                    #setter = getattr(self.visualiser, to_call, None)
                if setter is not None:
                    #try:
                    if parameter is not None and len(getargspec(setter).args) > 1:
                        setter(parameter)
                    else:
                        setter()
                    #except Exception as ex:
                     #   print(ex)
                    #    raise PreventUpdate()
        #try:
        graph = self.visualiser.build(graph_id=graph_id)
        graph = self.create_div(e_update_o["graph_id"].component_id, graph, className="col")
        graph = self.create_div(modify_graph_o["graph_container"].component_id, graph, className="col")

        node_types = self.visualiser.get_view_node_types()
        edge_types = self.visualiser.get_view_edge_types()

        typechoices = [{"label": _get_name(c), "value": c} for c in node_types]
        echoices = [{"label": _get_name(c), "value": c} for c in edge_types]
        figure, legend = self.visualiser.build(graph_id=graph_id, legend=True)
        legend = self.create_legend(legend)
        return [figure], legend,typechoices,echoices

        #except Exception as ex:
         #   print(ex)
           # raise PreventUpdate()

    def select_node(self,predicate,aes_c,aeo_c,elements,data,es_values,eo_values):
        hidden = {"display" : "none"}
        visible = {"display" : "block"}
        if predicate == []:
            return [],[],hidden,hidden
        if data is not None and data != []:
            changed_id = [p['prop_id'] for p in callback_context.triggered][0]
            if select_node_i["edge_subject"].component_id in changed_id:
                for node in data:
                    nid = int(node["id"])
                    res = self.visualiser.get_view_nodes(nid)
                    for e in es_values:
                        e["props"]["value"] = res.get_key()
            elif select_node_i["edge_object"].component_id in changed_id:
                for node in data:
                    nid = int(node["id"])
                    res = self.visualiser.get_view_nodes(nid)
                    for e in eo_values:
                        e["props"]["value"] = res.get_key()
                        
            return es_values,eo_values,visible,visible
        if predicate is not None:
            i_children = []
            o_children = []
            inps,outs = self.visualiser.get_io_nodes(predicate)
            for name,i in inps.items():
                nchoices = [{"label": _get_name(c.get_key()), "value": c.get_key()} for c in i]
                i_children += self.create_dropdown(name,nchoices,placeholder=name)
            for name,o in outs.items():
                nchoices = [{"label": _get_name(c.get_key()), "value": c.get_key()} for c in o]
                o_children += self.create_dropdown(name,nchoices,placeholder=name)
            return i_children,o_children,visible,visible
        else:
            return [],[],hidden,hidden

    def add_node(self,s_click,c_click,is_open,n_key,n_type,n_seq,n_desc):
        changed_id = [p['prop_id'] for p in callback_context.triggered][0].split(".")[0]
        if changed_id == "":
            return False, []
        if add_node_i["close_an"].component_id in changed_id:
            return False, []
        elif n_key != "":
            n_seq = None if n_seq == "" else n_seq
            n_desc = None if n_desc == "" else n_desc
            p,f = self.visualiser.get_standardised_nodes(n_key,n_type,n_seq,n_desc)
            for s,v in p.items():
                print(s,v)
            data = [{"entity" : n_key, "confidence" : "N/A", "comment" : "Local Name"}] + [{"entity" : s,"confidence" : str(v), "comment" : f[s]} for s,v in p.items()]
            return True,data
        return False,[]

    def modify_graph(self,n_select,e_click,n_data,n_type,n_seq,n_desc,e_subj,e_pred,e_obj):
        changed_id = [p['prop_id'] for p in callback_context.triggered][0]
        if None in self.visualiser.get_loaded_design_names():
            raise PreventUpdate()
        if n_select != [] and n_data != []:
            n_seq = None if n_seq == "" else n_seq
            n_desc = None if n_desc == "" else n_desc
            assert(len(n_select) == 1)
            print(n_data,n_select)
            n_key = n_data[n_select[0]]["entity"]
            self.visualiser.add_node(n_key,n_type,sequence=n_seq,description=n_desc)
            figure = self.visualiser.build(graph_id=graph_id)
            graph = self.create_div(e_update_o["graph_id"].component_id, figure)
            graph = self.create_div(modify_graph_o["graph_container"].component_id, graph, className="col")
            return graph
        if modify_graph_i["add_edge_submit"].component_id in changed_id:
            s_vals = {}
            e_vals = {}
            for s in e_subj:
                if s["props"]["value"] is None:
                    raise PreventUpdate()
                s_vals[s["props"]["id"]] = s["props"]["value"]
            for e in e_obj:
                if e["props"]["value"] is None:
                    raise PreventUpdate()
                e_vals[e["props"]["id"]] = e["props"]["value"]
            if e_subj is None or e_pred is None or e_obj is None:
                raise PreventUpdate()
            self.visualiser.add_edges(s_vals,e_vals,e_pred)
            figure = self.visualiser.build(graph_id=graph_id) 
            graph = self.create_div(e_update_o["graph_id"].component_id, figure)
            graph = self.create_div(modify_graph_o["graph_container"].component_id, graph, className="col")
            return graph
        else:
            raise PreventUpdate()
            
    def _create_editor(self):
        nkey = self.create_input(add_node_s["node_key"].component_id, placeholder="Node Key")
        add_node =  self.create_div("a_n_key", nkey, className="col") 
        ntype = self.create_dropdown(e_update_o["node_type"].component_id, [], placeholder="Node Type")
        add_node +=  self.create_div("a_n_type", ntype, className="col") 
        sub_a_n = self.create_button(add_node_i["submit_am"].component_id, "Add Node")
        add_node += self.create_line_break(10)
        add_node +=  self.create_div("a_n_submit", sub_a_n, className="col")
        meta_data = self.create_heading_5("node_metadata","Metadata (Optional)")
        meta_data += self.create_input(add_node_s["node_sequence"].component_id, placeholder="Sequence")
        meta_data += self.create_input(add_node_s["node_desc"].component_id, placeholder="Descriptions")
        add_node +=  self.create_div("a_n_meta", meta_data, className="col")

        subj_i = self.create_div(modify_graph_s["edge_subject"].component_id,[],className="col")
        subj_i_an = self.create_button(select_node_i["edge_subject"].component_id,"Add Selected Nodes")
        subj_i_an = self.create_div("edge_subject_an_div",subj_i_an,className="col")
        subj_i = self.create_div(select_node_o["node_subject_div"].component_id,subj_i + subj_i_an,className="row",style={"display" : "none"})
        add_edge =  self.create_div("a_e_subject", subj_i, className="col")
        pred_i = self.create_dropdown(e_update_o["edge_predicate"].component_id, [], placeholder="Predicate")
        add_edge += self.create_div("a_e_pred", pred_i, className="col") 

        obj_i = self.create_div(modify_graph_s["edge_object"].component_id,[],className="col")
        obj_i_an = self.create_button(select_node_i["edge_object"].component_id,"Add Selected Nodes")
        obj_i_an = self.create_div("edge_object_an_div",obj_i_an,className="col")
        obj_i = self.create_div(select_node_o["node_object_div"].component_id,obj_i + obj_i_an,className="row",style={"display" : "none"})
        add_edge +=  self.create_div("a_e_obj", obj_i, className="col")

        sub_i = self.create_button(modify_graph_i["add_edge_submit"].component_id, "Add Edge")
        add_edge +=  self.create_div("a_e_submit", sub_i, className="col")
        add_edge += self.create_line_break(10)

        add_node = self.create_div("add_node_div",add_node,className="row")
        add_edge = self.create_div("add_edge_div",add_edge,className="row")
        acc_elements = [("Add Node", add_node), ("Add Edge",add_edge)]
        return self.create_accordion("editor_accordion", acc_elements)

    def _create_form_elements(self, visualiser, style={}, id_prefix=""):
            default_options = [visualiser.set_network_mode,
                            visualiser.set_full_graph_view,
                            visualiser.set_concentric_layout,
                            visualiser.add_node_no_labels,
                            visualiser.add_edge_no_labels,
                            visualiser.add_standard_node_color,
                            visualiser.add_standard_edge_color]

            options = self._generate_options(visualiser)
            removal_words = ["Add", "Set"]
            elements = []
            identifiers = {}
            docstring = []
            variable_input_list_map = OrderedDict()
            for k, v in options.items():
                name = self._beautify_name(k)
                identifier = id_prefix + "_" + k
                element = []

                if isinstance(v, (int, float)):
                    min_v = int(v/1.7)
                    max_v = int(v*1.7)
                    default_val = int((min_v + max_v) / 2)
                    step = 1

                    element += (self.create_heading_6("", name) +
                                self.create_slider(identifier, min_v, max_v, default_val=default_val, step=step))
                    identifiers[k] = Input(identifier, "value")
                    variable_input_list_map[identifier] = [min_v, max_v]

                elif isinstance(v, dict):
                    removal_words = removal_words + \
                        [word for word in name.split(" ")]
                    inputs = []
                    default_button = None
                    for k1, v1 in v.items():
                        label = self._beautify_name(k1)
                        label = "".join(
                            "" if i in removal_words else i + " " for i in label.split())
                        inputs.append({"label": label, "value": k1})
                        if v1 in default_options:
                            default_button = k1

                    variable_input_list_map[identifier] = [
                        l["value"] for l in inputs]
                    element = (self.create_heading_6(k, name) +
                            self.create_radio_item(identifier, inputs, value=default_button))
                    identifiers[k] = Input(identifier, "value")
                    docstring += self._build_docstring(name, v)

                breaker = self.create_horizontal_row(False)
                elements = elements + \
                    self.create_div(identifier + "_contamanual_toolbariner",
                                    element, style=style)
                elements = elements + breaker

            export_div = self.create_div(
                export_modal_o["data"].component_id, [])
            export_modal = self.create_modal(export_modal_o["id"].component_id,
                                            export_modal_i["close_export"].component_id,
                                            "Export", export_div)

            exports = self.create_heading_4("export_img_heading", "Image Export")
            for e_input in export_img_i:
                exports += self.create_button(e_input.component_id,
                                            className="export_img_button")
                exports += self.create_line_break()
            exports += self.create_heading_4("export_data_heading", "Data Export")
            for sf in visualiser._builder.view.get_save_formats():
                export_modal_i[sf] = Input(sf, "n_clicks")
            for e_input in export_modal_i.values():
                if e_input.component_id == "close_export":
                    continue
                exports += self.create_button(e_input.component_id,
                                            className="export_img_button")
                exports += self.create_line_break()
            export_div = self.create_div(
                "export_data_container", exports, style=style)

            return (elements + export_div +  export_modal, identifiers, variable_input_list_map)

    def _generate_options(self, visualiser):
        blacklist_functions = ["empty_graph",
                               "build",
                               "mode",
                               "view",
                               "node_size",
                               "edge_color",
                               "node_color",
                               "copy_settings",
                               "get_design_names",
                               "edge_shape",
                               "edge_text",
                               "node_shape",
                               "node_text",
                               "set_design_names",
                               "add_edges",
                               "preset",
                               "get_nodes",
                               "get_edge_labels",
                               "get_load_predicates",
                               "add_node",
                               "get_view_node",
                               "get_io_nodes",
                               "get_standardised_nodes"]

        options = {"view": {},
                   "layout": {}}

        for func_str in dir(visualiser):
            if func_str[0] == "_":
                continue
            func = getattr(visualiser, func_str, None)

            if func is None or func_str in blacklist_functions or not callable(func):
                continue
            if "mode" in func_str:
                continue
            if len(signature(func).parameters) > 0:
                # When there is parameters a slider will be used.
                # Some Paramterised setters will return there default val if one isnt provided.
                default_val = func()
                if default_val is None:
                    default_val = 1
                options[func_str] = default_val
            else:
                # When no params radiobox.
                if func_str.split("_")[-1] == "preset":
                    option_name = "preset"

                elif func_str.split("_")[-1] == "view":
                    option_name = "view"

                elif func_str.split("_")[-1] == "mode":
                    option_name = "mode"

                elif func_str.split("_")[-1] == "layout":
                    option_name = "layout"

                elif func_str.split("_")[-1] == "connect":
                    option_name = "connect"

                elif "node" in func_str:
                    option_name = "node" + "_" + func_str.split("_")[-1]

                elif "edge" in func_str:
                    option_name = "edge" + "_" + func_str.split("_")[-1]
                elif func_str.split("_")[-1] == "level":
                    option_name = "detail"
                else:
                    option_name = "misc"

                if option_name not in options.keys():
                    options[option_name] = {func_str: func}
                else:
                    options[option_name][func_str] = func
        return options

    def _beautify_name(self, name):
        name_parts = name.split("_")
        name = "".join([p.capitalize() + " " for p in name_parts])
        return name

    def _build_docstring(self, doc_name, functions):
        doc_body = self.create_heading_4(doc_name, doc_name)
        for name, function in functions.items():
            func_data = self.create_heading_5(
                name + "_doc_heading", self._beautify_name(name))
            func_doc = function.__doc__
            if func_doc is None:
                func_doc = "No Information."
            func_doc = func_doc.lstrip().rstrip().replace("    ", "")
            func_data += self.create_paragraph(func_doc)
            doc_body += self.create_div(name + "_doc",
                                        func_data) + self.create_line_break()

        doc_body += self.create_horizontal_row(False)
        return self.create_div(doc_name + "_container", doc_body)

def _get_name(subject):
    split_subject = _split(str(subject))
    if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
        return split_subject[-2]
    else:
        return split_subject[-1]


def _split(uri):
    return re.split('#|\/|:', uri)
