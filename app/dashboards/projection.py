from dash.dependencies import Input,State
from dash.exceptions import PreventUpdate
from inspect import signature, getargspec
from dash.dependencies import Input,Output
from dash.exceptions import PreventUpdate
from dash import callback_context

from app.dashboards.abstract_dashboard.utility.callback_structs import *
from app.dashboards.abstract_dashboard.abstract import AbstractDash
from app.dashboards.visual.projection import ProjectionVisual

assets_ignore = '.*bootstrap.*'


class ProjectionDash(AbstractDash):
    def __init__(self, name, server, graph):
        super().__init__(ProjectionVisual(graph), name, server,
                         "/gds/", assets_ignore=assets_ignore)
        self._build_app()

    def _build_app(self):
        f_ele, ids = self._create_f_ele(self.visualiser, id_prefix)
        update_inputs = ids

        # Projection
        # RAW
        p_message = self.create_div(project_out["message"].component_id, [])
        raw = (self.create_text_area(project_states["raw_input"].component_id) + 
              self.create_button(project_inp["raw_submit"].component_id, "Submit"))

        # Native
        n = [{"label": c, "value": c} for c in self.visualiser.get_node_labels()]
        e = [{"label": c, "value": c} for c in self.visualiser.get_edge_labels()]
        np = [{"label": c, "value": c} for c in self.visualiser.get_node_property_names()]
        ep = [{"label": c, "value": c} for c in self.visualiser.get_edge_property_names()]
        native = (self.create_input(project_states["native_name"].component_id, placeholder="Graph Name") + 
                 self.create_dropdown(project_states["node"].component_id, n, multi=True, placeholder="Nodes") + 
                 self.create_dropdown(project_states["edge"].component_id, e, multi=True, placeholder="Edges") + 
                 self.create_dropdown(project_states["node_properties"].component_id, np, multi=True, placeholder="Node Properties") + 
                 self.create_dropdown(project_states["edge_properties"].component_id, ep, multi=True, placeholder="Edge Properties"))
        native = (self.create_div("native_div", native) + 
                  self.create_line_break(5) + 
                  self.create_button(project_inp["native_submit"].component_id, "Submit"))

        # Preset
        pn = [{"label": c, "value": c} for c in self.visualiser.get_project_preset_names()]
        preset = (self.create_input(project_states["preset_name"].component_id, placeholder="Graph Name") + 
                  self.create_dropdown(project_states["preset_graph"].component_id, pn, placeholder="Projection"))
        preset = (self.create_div("preset_div", preset) + 
                  self.create_div(project_params_out.component_id,[]) + 
                  self.create_line_break(10) + 
                  self.create_button(project_inp["preset_submit"].component_id, "Submit"))
        acc_elements = [("Raw", raw), 
                        ("Native", native), 
                        ("Preset", preset)]
        proj_accordion = self.create_accordion("proj_accordion", acc_elements)

        # Load
        pn = [{"label": c, "value": c} for c in self.visualiser.get_project_graph_names()]
        inp = (self.create_dropdown(project_load_input.component_id, pn) + 
              self.create_line_break(10))
        projection_vis = self.create_div("projection_vis", inp)

        # Procedures
        proc_struct = self.visualiser.get_procedures_info()
        proc_elements = []
        for name,funcs in proc_struct.items():
            pt_eles = []
            for func,params in funcs.items():
                param_b = []
                for p,t in params.items():
                    param_id = f'{func}/{p}'
                    if t is not None:
                        param_b += self.create_dropdown(param_id, t,placeholder=p) 
                        plo_inp_box.append(Output(param_id,"options"))
                    else:
                        param_b += self.create_input(param_id,placeholder=p)
                    procedure_state.append(State(param_id,"value"))
                    
                button_id = f'{name}/{func}'
                param_b += (self.create_line_break(10) + self.create_button(button_id,"Run Procedure"))
                procedure_input.append(Input(button_id,"n_clicks"))
                pt_eles.append((func,param_b))
            proc_elements.append((name,self.create_accordion(name+"acc",pt_eles)))
        proc_acc = self.create_accordion(project_load_output["procs"].component_id,proc_elements,style={"display":"none"})
        ni = self.create_div(project_load_output["info"].component_id,[])
        procedure_out = self.create_div(procedure_output[0].component_id,[])
        # Top-Level 
        acc_elements = [("Node Information", ni), 
                        ("Run Procedures", proc_acc),
                        ("Procedure Outputs", procedure_out)]

        procedures = self.create_accordion("proc_accordion", acc_elements)

        acc_elements = [("Graph Projection", p_message+proj_accordion),
                        ("Load", projection_vis),
                        ("Procedures", procedures)]
        accordion = self.create_accordion("accordion", acc_elements)
        accordion = self.create_div("", accordion, className="col min-vw-100")
        accordion = self.create_div("", accordion, className="row")

        # Graph.
        figure, legend, datatable = self.visualiser.build(graph_id=graph_id, datatable=True, legend=True)
        graph = self.create_div(update_outputs["graph_id"].component_id, [figure], className="col")
        graph = self.create_div(project_load_output["graph_id"].component_id, graph)
        legend = self.create_legend(legend)
        legend = self.create_div(update_outputs["legend_id"].component_id, legend, className="col sidebar")
        form_div = self.create_div(graph_type_outputs["id"].component_id, f_ele)
        options = self.create_sidebar(not_modifier_identifiers["sidebar_id"], "Options", form_div, className="col sidebar")
        graph = self.create_div("cypher-graph", options+graph+legend, className="row")

        # DataTable
        datatable = self.create_heading_4("no_graph", "No Loaded Graph.")
        datatable = self.create_div(project_load_output["datatable"].component_id, datatable, className="col")
        datatable = self.create_div("datatable-row", datatable, className="row")


        def update_graph_inner(*args):
            return self.update_graph(args)

        def project_params_inner(preset):
            return self.project_params(preset)

        def project_inner(raw_click, native_click, preset_click, raw_value, name, nodes, edges, n_props, e_props,preset_name,preset_graph,preset_params):
            return self.project(raw_click, native_click, preset_click, raw_value, name, nodes, edges, n_props, e_props,preset_name,preset_graph,preset_params)
        
        def procedure_inner(*args):
            return self.procedure(args)

        def load_inner(value):
            return self.load(value)

        self.add_callback(project_params_inner, [project_params_inp], [project_params_out])
        self.add_callback(project_inner, list(project_inp.values()), list(project_out.values()), list(project_states.values()))
        self.add_callback(load_inner, [project_load_input], list(project_load_output.values())+plo_inp_box)
        self.add_callback(update_graph_inner, list(update_inputs.values()), list(update_outputs.values()))
        self.add_callback(procedure_inner, procedure_input, procedure_output, procedure_state)
        self.app.layout = self.create_div("main", accordion+graph+datatable, className="container min-vw-100 py-4")[0]
        self.build()

    def _create_datatable(self,id,struct):
        return self.create_complex_table(id, [{"name": str(i), "id": str(i)} for i in struct[0].keys()], struct)

    def project_params(self,preset):
        if preset is None:
            raise PreventUpdate()
        params = self.visualiser.get_project_preset_parameters(preset)
        children = []
        for name,param in params.items():
            print(name,param)
            c = [{"label": c, "value": c} for c in param]
            children += self.create_dropdown(name,c,placeholder=name)
        return [children]

    def project(self, raw_click, native_click, preset_click, raw_value, name, nodes, edges, n_props, e_props,preset_name,preset_graph,preset_params):
        changed_id = [p['prop_id']
                      for p in callback_context.triggered][0].split(".")[0]
        if changed_id == "":
            raise PreventUpdate()
        if changed_id == project_inp["raw_submit"].component_id:
            try:
                self.visualiser.run_cypher(raw_value)
                message = f"Projected Graph"
            except Exception as ex:
                message = f'Error: {ex}'
        elif changed_id == project_inp["native_submit"].component_id:
            if not nodes:
                nodes = "*"
            if not edges:
                edges = "*"
            try:
                self.visualiser.project_graph(name, nodes, edges, n_props, e_props)
                message = f"Projected Graph"
            except Exception as ex:
                message = f'Error: {ex}'
        elif changed_id == project_inp["preset_submit"].component_id:
            params = {}
            for param in preset_params:
                if param["props"]["value"] is not None:
                    params[param["props"]["id"]] = param["props"]["value"]
            try:
                self.visualiser.project_preset(preset_name,preset_graph,**params)
                message = "Projected Graph"
            except Exception as ex:
                message = f'Error: {ex}'


        message = self.create_heading_5("projection_message", message)
        choices = [{"label": c, "value": c} for c in self.visualiser.get_project_graph_names()]
        return choices, message

    def load(self, graph_name):
        if not graph_name or not isinstance(self.visualiser, ProjectionVisual):
            raise PreventUpdate()
        #try:
        self.visualiser.set_projection_graph(graph_name)
        self.visualiser.set_projection_view()
        figure,dt = self.visualiser.build(graph_id=graph_id,datatable=True)
        d = self.create_div(update_outputs["graph_id"].component_id, figure, className="col")
        dt = (self._create_datatable("project-meta",self.visualiser.get_graph_metadata()) + self._create_datatable("project-data",dt))
        project_struct = self.visualiser.get_project_info()
        ni = self._create_datatable(project_load_output["info"].component_id,project_struct)
        params = [n.component_id.split("/")[-1] for n in plo_inp_box]
        box_values = self.visualiser.get_parameter_types(params)
        return d,dt,ni,{"style":"block"},*box_values
        #except Exception as ex:
        #    print(ex)
         #   raise PreventUpdate()

    def procedure(self,*args):
        if not isinstance(self.visualiser, ProjectionVisual):
            raise PreventUpdate()
        ci = [p['prop_id'] for p in callback_context.triggered][0].split(".")[0]
        if len(ci) == 0:
            raise PreventUpdate()
        parts = ci.split("/")
        assert(len(parts) == 2)
        module,func = parts
        args = args[0]
        states_arg = args[len(procedure_input):]
        params = {}
        for index,arg in enumerate(states_arg):
            if arg is not None:
                state = procedure_state[index]
                param = state.component_id.split("/")[-1]
                params[param] = arg
        res = self.visualiser.run_procedure(module,func,params)
        if len(res) == 0:
            return self.create_heading_4("nrf","No Results Found.")
        return self._create_datatable("procedure_out",res)

    def update_graph(self, *args):
        if not isinstance(self.visualiser, ProjectionVisual):
            raise PreventUpdate()
        args = args[0]
        for index, setter_str in enumerate(args):
            if setter_str is not None:
                try:
                    setter = getattr(self.visualiser, setter_str, None)
                    parameter = None
                except TypeError:
                    # Must be a input elemestyleementation this is tough.
                    to_call = list(update_inputs.keys())[index]
                    parameter = setter_str
                    setter = getattr(self.visualiser, to_call, None)
                if setter is not None:
                    try:
                        if parameter is not None and len(getargspec(setter).args) > 1:
                            setter(parameter)
                        else:
                            setter()
                    except Exception as ex:
                        print(ex)
                        raise PreventUpdate()
        try:
            figure, legend = self.visualiser.build(
                graph_id=graph_id, legend=True)
            legend = self.create_legend(legend)
            return [figure], legend
        except Exception as ex:
            print(ex)
            raise PreventUpdate()

    def _create_f_ele(self, visualiser, id_prefix):
        default_options = [visualiser.set_network_mode,
                           visualiser.set_no_view,
                           visualiser.set_cola_layout,
                           visualiser.add_node_name_labels,
                           visualiser.add_edge_name_labels,
                           visualiser.add_standard_node_color,
                           visualiser.add_standard_edge_color]

        options = self._generate_options(visualiser)
        removal_words = ["Add", "Set"]
        elements = []
        identifiers = {}
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

            breaker = self.create_horizontal_row(False)
            elements = (elements + 
                       self.create_div(identifier + "_contamanual_toolbariner", element) + 
                       breaker)
        export_div = self.create_div(
            export_modal_outputs["data"].component_id, [])
        export_modal = self.create_modal(export_modal_outputs["id"].component_id,
                                         export_modal_inputs["close_export"].component_id,
                                         "Export", export_div)
        exports = self.create_heading_4("export_img_heading", "Image Export")
        for e_input in export_img_inputs:
            exports += self.create_button(e_input.component_id,
                                          className="export_img_button")
            exports += self.create_line_break()
        exports += self.create_heading_4("export_data_heading", "Data Export")
        for sf in visualiser._builder.view.get_save_formats():
            export_modal_inputs[sf] = Input(sf, "n_clicks")
        for e_input in export_modal_inputs.values():
            if e_input.component_id == "close_export":
                continue
            exports += self.create_button(e_input.component_id,
                                          className="export_img_button")
            exports += self.create_line_break()
        export_div = self.create_div("export_data_container", exports)
        return (elements + export_div + export_modal, identifiers)

    def _generate_options(self, visualiser):
        blacklist_functions = ["build",
                               "mode",
                               "view",
                               "edge_pos",
                               "node_text",
                               "edge_text",
                               "node_color",
                               "edge_color",
                               "edge_shape",
                               "node_size",
                               "node_shape",
                               "layout",
                               "copy_settings",
                               "set_projection_graph",
                               "get_project_graph_names",
                               "project_graph",
                               "get_graph_metadata",
                               "get_edge_property_names",
                               "get_node_property_names",
                               "get_edge_properties",
                               "run_cypher",
                               "get_node_properties",
                               "get_edge_labels",
                               "get_node_labels",
                               "get_project_preset_names"]

        options = {"mode": {},
                   "layout": {}}

        for func_str in dir(visualiser):
            if func_str[0] == "_":
                continue
            func = getattr(visualiser, func_str, None)
            if func is None or func_str in blacklist_functions or not callable(func):
                continue
            if func_str.split("_")[-1] == "preset":
                continue

            elif func_str.split("_")[-1] == "view":
                continue

            if len(signature(func).parameters) > 0:
                # When there is parameters a slider will be used.
                # Some Paramterised setters will return there default val if one isnt provided.
                try:
                    default_val = func()
                except TypeError:
                    continue
                if default_val is None:
                    default_val = 1
                options[func_str] = default_val
            else:
                # When no params radiobox.
                if func_str.split("_")[-1] == "mode":
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
