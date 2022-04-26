from dash.exceptions import PreventUpdate
from inspect import signature, getargspec
from dash.dependencies import Input
from dash.exceptions import PreventUpdate
from neo4j.exceptions import CypherSyntaxError
from dash import callback_context

from app.dashboards.abstract_dashboard.utility.callback_structs import *
from app.dashboards.visual.abstract import AbstractVisual
from app.dashboards.abstract_dashboard.abstract import AbstractDash
from app.dashboards.visual.cypher import CypherVisual

assets_ignore = '.*bootstrap.*'

class CypherDash(AbstractDash):
    def __init__(self, name, server, graph):
        super().__init__(CypherVisual(graph), name, server,
                         "/cypher/", assets_ignore=assets_ignore)
        self._build_app()

    def _build_app(self):
        form_elements, identifiers = self._create_form_elements(self.visualiser, id_prefix=id_prefix)
        update_inputs = identifiers

        # Cypher Bar Callback.
        default_qry = self.visualiser.default_query()
        inp = self.create_input(cypher_state.component_id, default_qry,className="form-control border-end-0 border")
        button = self.create_button(cypher_input["submit"].component_id,"Submit",className="",type="button") 
        input_group = self.create_div("cypher_input",inp+button,className="input-group")
        cypher_col = self.create_div("cypher_col",input_group,className="col")
        cypher_bar = self.create_div("cypher",cypher_col,className="row")

        # Graph.
        self.visualiser.set_default_preset()
        figure,legend,datatable = self.visualiser.build(graph_id=graph_id,datatable=True,legend=True)
        graph = self.create_div(update_outputs["graph_id"].component_id, [figure], className="col")
        graph = self.create_div(cypher_output["graph_id"].component_id, graph)
        legend = self.create_legend(legend)
        legend = self.create_div(update_outputs["legend_id"].component_id,legend, className="col sidebar")
        form_div = self.create_div(graph_type_outputs["id"].component_id, form_elements)
        options = self.create_sidebar(not_modifier_identifiers["sidebar_id"], "Options", form_div, className="col sidebar")
        graph = self.create_div("cypher-graph",options+graph+legend,className="row")

        # DataTable
        datatable = self._create_datatable(datatable)
        datatable = self.create_div(cypher_output["datatable_id"].component_id,datatable,className="col")
        datatable = self.create_div("datatable-row",datatable,className="row")

        self.app.layout = self.create_div("main", cypher_bar+graph+datatable, className="container shadow min-vw-100 py-4")[0]

        for sf in self.visualiser._builder.view.get_save_formats():
            export_modal_inputs[sf] = Input(sf, "n_clicks")

        def update_graph_cypher_inner(button,state):
            return self.update_graph_cypher(button,state)
        def update_graph_toolbar_inner(*args):
            return self.update_graph_toolbar(args)
        def export_img_inner(*args):
            return self.export_graph_img(*args)
        def export_modal_inner(*args):
            return self.export_modal(*args)

        self.add_callback(update_graph_toolbar_inner, list(update_inputs.values()), list(update_outputs.values()))
        self.add_callback(update_graph_cypher_inner, list(cypher_input.values()), list(cypher_output.values()),cypher_state)
        self.add_callback(export_img_inner,export_img_inputs, export_img_outputs)
        self.add_callback(export_modal_inner, list(export_modal_inputs.values()), list(export_modal_outputs.values()), export_modal_states)
        self.build()
        

    def _create_datatable(self,struct):
        if len(struct) == 0:
            return self.create_heading_4("no_results","No Results Found.")
        return self.create_complex_table("datatable_t",[{"name": str(i), "id": str(i)} for i in struct[0].keys()],struct)

    def update_graph_cypher(self, n_clicks,query):
        if not isinstance(self.visualiser, CypherVisual):
            raise PreventUpdate()
        try:
            self.visualiser.set_query(query)
            try:
                figure,datatable = self.visualiser.build(graph_id=graph_id,height=80,width=80,datatable=True)
                graph = self.create_div(update_outputs["graph_id"].component_id, [figure], className="col")
            except CypherSyntaxError as ex:
                return self.create_heading_4("cypher-syntax-error",f"Syntax Error: {ex}"),[]
            datatable = self._create_datatable(datatable)
            return graph,datatable
        except Exception as ex:
            print(ex)
            raise PreventUpdate()

    def update_graph_toolbar(self, *args):
        if not isinstance(self.visualiser, AbstractVisual):
            raise PreventUpdate()
        args = args[0]
        for index, setter_str in enumerate(args):
            if setter_str is not None:
                try:
                    setter = getattr(self.visualiser, setter_str, None)
                    parameter = None
                except TypeError:
                    # Must be a input element rather than a checkbox.
                    # With annonymous implementation this is tough.
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
                graph_id=graph_id, legend=True,height=80,width=80)
            legend = self.create_legend(legend)
            return [figure], legend
        except Exception as ex:
            print(ex)
            raise PreventUpdate()

    def export_graph_img(self, get_jpg_clicks, get_png_clicks, get_svg_clicks):
        action = 'store'
        input_id = None
        ctx = callback_context
        if ctx.triggered:
            input_id = ctx.triggered[0]["prop_id"].split(".")[0]
            if input_id != "tabs":
                action = "download"
        return {'type': input_id, 'action': action}

    def export_modal(self, *args):
        changed_id = [p['prop_id']
                      for p in callback_context.triggered][0].split(".")[0]
        if changed_id == "":
            return False, []
        if export_modal_inputs["close_export"].component_id in changed_id:
            return False, []
        else:
            children = []
            try:
                data = self.visualiser._builder.view.generate(changed_id)
                children += self.create_text_area("export-data",
                                                  value=data, disabled=True)
            except KeyError:
                pass
            return True, children

    def _create_form_elements(self, visualiser, style={}, id_prefix=""):
            default_options = [visualiser.set_network_mode,
                            visualiser.set_cypher_view,
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
                elements = elements + \
                    self.create_div(identifier + "_contamanual_toolbariner",element, style=style)
                elements = elements + breaker
            export_div = self.create_div(
                export_modal_outputs["data"].component_id, [])
            export_modal = self.create_modal(export_modal_outputs["id"].component_id,
                                            export_modal_inputs["close_export"].component_id,
                                            "Export", export_div)
            exports = self.create_heading_4("export_img_heading", "Image Export")
            for e_input in export_img_inputs:
                exports += self.create_button(e_input.component_id,className="export_img_button")
                exports += self.create_line_break()
            exports += self.create_heading_4("export_data_heading", "Data Export")
            for sf in visualiser._builder.view.get_save_formats():
                export_modal_inputs[sf] = Input(sf, "n_clicks")
            for e_input in export_modal_inputs.values():
                if e_input.component_id == "close_export":
                    continue
                exports += self.create_button(e_input.component_id,className="export_img_button")
                exports += self.create_line_break()
            export_div = self.create_div("export_data_container", exports, style=style)
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
                               "connect",
                               "set_query",
                               "preset",
                               "default_query",
                               "set_cypher_view"]

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
                default_val = func()
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