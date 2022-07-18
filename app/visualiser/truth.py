import re
from inspect import signature, getargspec
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import callback_context

from app.visualiser.abstract_dashboard.utility.callback_structs import *
from app.visualiser.visual.truth import TruthVisual
from app.visualiser.abstract_dashboard.abstract import AbstractDash

assets_ignore = '.*bootstrap.*'

class TruthDash(AbstractDash):
    def __init__(self, name, server, graph):
        super().__init__(TruthVisual(graph), name, server,
                         "/truth/", assets_ignore=assets_ignore)
        self._build_app()
        
    def _build_app(self):
        # Add Options
        form_elements, identifiers, maps = self._create_form_elements(self.visualiser, id_prefix=id_prefix)
        del maps["cyto_preset"]
        preset_identifiers, identifiers, preset_output, preset_state = self._generate_inputs_outputs(identifiers)
        update_i.update(identifiers)
        preset_i.update(preset_identifiers)
        preset_o.update(preset_output)
        
        form_div = self.create_div(graph_type_o["id"].component_id, form_elements)
        options = self.create_sidebar(not_modifier_identifiers["sidebar_id"], "Options", form_div, className="col sidebar")
        figure = self.visualiser.empty_graph(graph_id)
        graph = self.create_div(update_o["graph_id"].component_id, [figure], className="col")
        graph = self.create_div(load_o.component_id, graph)
        legend = self.create_div(update_o["legend_id"].component_id,[], className="col sidebar")
        elements = options+graph+legend
        container = self.create_div("row-main", elements, className="row flex-nowrap no-gutters")
        self.app.layout = self.create_div("main", container, className="container-fluid")[0]

        for sf in self.visualiser._builder.view.get_save_formats():
            export_modal_i[sf] = Input(sf, "n_clicks")

        # Bind the callbacks
        def update_graph_inner(*args):
            return self.update_graph(args)

        def export_img_inner(*args):
            return self.export_graph_img(*args)

        
        self.add_callback(update_graph_inner, update_i.values(), update_o.values())
        self.add_callback(export_img_inner,export_img_i, export_img_o)
        self.build()

    def update_graph(self, *args):
        if not isinstance(self.visualiser, DesignVisual):
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
                    to_call = list(update_i.keys())[index]
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

    def export_graph_img(self, get_jpg_clicks, get_png_clicks, get_svg_clicks):
        action = 'store'
        input_id = None
        ctx = callback_context
        if ctx.triggered:
            input_id = ctx.triggered[0]["prop_id"].split(".")[0]
            if input_id != "tabs":
                action = "download"
        else:
            raise PreventUpdate()
        return [{'type': input_id, 'action': action}]

    def _generate_node_edge_tables(self, builder):
        view = builder.view
        nodes = builder.view.nodes()
        edges = builder.view.edges()

        e_cols = [{"name": k, "id": k} for k in ["node", "edge", "vertex"]]
        e_data = [{"node": e.n.name, "edge":e.name,"vertex": e.v.name} for e in edges]
        n_cols = [{"name": k, "id": k} for k in ["Node", "Degree", "Pagerank", "Degree Centrality",
                                                 "Closeness Centrality", "Betweenness Centrality", "Is Isolated",
                                                 "Number Of Cliques", "Clustering", "Square Clustering"]]
        n_data = []
        pagerank = view.pagerank()
        degree_centrality = view.degree_centrality()
        closeness_centrality = view.closeness_centrality()
        betweenness_centrality = view.betweenness_centrality()
        number_cliques = view.number_of_cliques()
        clustering = view.clustering()
        square_clustering = view.square_clustering()
        for node in nodes:
            nd = {"Node": node.name}
            nd["Degree"] = view.degree(node.id)
            nd["Pagerank"] = pagerank[node.id]
            nd["Degree Centrality"] = degree_centrality[node.id]
            nd["Closeness Centrality"] = closeness_centrality[node.id]
            nd["Betweenness Centrality"] = betweenness_centrality[node.id]
            nd["Is Isolated"] = view.is_isolate(node.id)
            nd["Number Of Cliques"] = number_cliques[node.id]
            nd["Clustering"] = clustering[node.id]
            nd["Square Clustering"] = square_clustering[node.id]
            n_data.append(nd)
        return n_cols, n_data, e_cols, e_data

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

        ds_button = self.create_div(
            docs_modal_i["open_doc"].component_id, [], className="help-tip col")
        docstrings = self.create_modal(docs_modal_o["id"].component_id,
                                       docs_modal_i["close_doc"].component_id,
                                       "Options Documentation", docstring)

        info_button = self.create_div(
            info_modal_i["open_info"].component_id, [], className="info-tip col")
        info_text = self.create_div(
            info_modal_o["info"].component_id, [])
        info_modal = self.create_modal(
            info_modal_o["id"].component_id, info_modal_i["close_info"].component_id, "Graph Statistics", info_text)

        export_div = self.create_div(
            export_modal_o["data"].component_id, [])
        export_modal = self.create_modal(export_modal_o["id"].component_id,
                                         export_modal_i["close_export"].component_id,
                                         "Export", export_div)
        adv_button = self.create_div(
            adv_modal_i["open_adv"].component_id, [], className="adv-tip col")
        adv_opn = self.create_div(adv_modal_o["form"].component_id, [])
        adv_options = self.create_modal(adv_modal_o["adv_modal_id"].component_id,
                                        adv_modal_i["close_adv"].component_id,
                                        "Advanced Options", adv_opn,
                                        adv_modal_i['submit_adv'].component_id)

        manual_button = self.create_div(
            man_tool_i["open_man"].component_id, [], className="manual-tip col")
        eo = self.create_div('', ds_button + adv_button +
                             manual_button + info_button, className="row")
        r = self.create_horizontal_row(False)
        extra_options = self.create_div("", eo + r, className="container")

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

        return (extra_options + elements + export_div +
                docstrings + export_modal + adv_options + info_modal, identifiers, variable_input_list_map)

    def _beautify_name(self, name):
        name_parts = name.split("_")
        name = "".join([p.capitalize() + " " for p in name_parts])
        return name

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
                               "set_design_names"]

        options = {"preset": {},
                   "mode": {},
                   "view": {},
                   "layout": {}}

        for func_str in dir(visualiser):
            if func_str[0] == "_":
                continue
            func = getattr(visualiser, func_str, None)

            if func is None or func_str in blacklist_functions or not callable(func):
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

    def _generate_inputs_outputs(self, identifiers):
        preset_identifiers = {"preset": identifiers["preset"]}
        del identifiers["preset"]
        outputs = {k: Output(v.component_id, v.component_property)
                   for k, v in identifiers.items()}
        states = {k: State(v.component_id, v.component_property)
                  for k, v in identifiers.items()}
        return preset_identifiers, identifiers, outputs, states

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


def _derive_form(form):
    used_types = ["Input", "Slider", "Dropdown"]
    elements = {}
    children = form[0]["props"]["children"][0]["props"]["children"]
    for c in children:
        element = c["props"]
        e_type = c["type"]
        if e_type not in used_types:
            continue
        identifier = element["id"]
        value = element["value"]
        if value is None or value == 0.5:
            continue
        elements[identifier] = value
    return elements
