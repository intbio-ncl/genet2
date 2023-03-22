import re
from inspect import signature, getargspec
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import callback_context

from app.visualiser.abstract_dashboard.utility.callback_structs import *
from app.visualiser.visual.truth import TruthVisual
from app.visualiser.abstract_dashboard.abstract import AbstractDash

assets_ignore = '.*bootstrap.*'
hFalse = False
class TruthDash(AbstractDash):
    def __init__(self, name, server, graph):
        super().__init__(TruthVisual(graph), name, server,
                         "/truth/", assets_ignore=assets_ignore)
        self._build_app()
        
    def _build_app(self):
        update_i.clear()
        preset_i.clear()
        preset_o.clear()
        form_elements, identifiers, maps = self._create_form_elements(
            self.visualiser, id_prefix=id_prefix)
        del maps["cyto_preset"]
        preset_identifiers, identifiers, preset_output, preset_state = self._generate_inputs_outputs(
            identifiers)
        
        update_i.update(identifiers)
        preset_i.update(preset_identifiers)
        preset_o.update(preset_output)

        manual = self._create_manual_toolbar()
        form_div = self.create_div(graph_type_o["id"].component_id, form_elements)
        options = self.create_sidebar(not_modifier_identifiers["sidebar_id"], "Options", form_div, className="col sidebar")
        figure, legend = self.visualiser.build(graph_id=graph_id, legend=True)
        graph = self.create_div(update_o["graph_id"].component_id, figure, className="col")
        graph = self.create_div(load_o.component_id, graph)
        legend = self.create_legend(legend)
        legend = self.create_div(update_o["legend_id"].component_id,legend, className="col sidebar")
        elements = options+graph+legend+manual
        container = self.create_div("row-main", elements, className="row flex-nowrap no-gutters")
        self.app.layout = self.create_div("main",container, className="container-fluid")[0]

        for sf in self.visualiser._builder.view.get_save_formats():
            export_modal_i[sf] = Input(sf, "n_clicks")

        # Bind the callbacks

        def update_preset_inner(preset_name, *states):
            return self.update_preset(preset_name, maps, states)

        def update_graph_inner(*args):
            return self.update_graph(args)

        def docs_modal_inner(*args):
            return self.docs_modal(*args)

        def info_modal_inner(*args):
            return self.info_modal(*args)

        def man_tool_inner(*args):
            return self.man_modal(*args)

        def modify_node_inner(t_delete, t_merge, elems, data):
            return self.modify_nodes(t_delete, t_merge, elems, data)

        def advanced_modal_inner(*args):
            return self.advanced_modal(*args)

        def export_img_inner(*args):
            return self.export_graph_img(*args)

        def export_modal_inner(*args):
            return self.export_modal(*args)

        def background_color_inner(*args):
            return self.background_color(*args)

        def label_color_inner(*args):
            return self.label_color(*args)
        

        self.add_callback(update_graph_inner, update_i.values(), update_o.values())
        self.add_callback(update_preset_inner, preset_i.values(), preset_o.values(), preset_state.values())
        self.add_callback(docs_modal_inner, docs_modal_i.values(), docs_modal_o.values(), doc_modal_s)
        self.add_callback(info_modal_inner, info_modal_i.values(), info_modal_o.values(), info_modal_s)
        self.add_callback(man_tool_inner, man_tool_i.values(), man_tool_o.values(), man_tool_s)
        self.add_callback(modify_node_inner, modify_node_i.values(),modify_node_o, modify_node_s)
        self.add_callback(advanced_modal_inner, adv_modal_i.values(), adv_modal_o.values(), adv_modal_s)
        self.add_callback(export_img_inner,export_img_i, export_img_o)
        self.add_callback(export_modal_inner, export_modal_i.values(), export_modal_o.values(), export_modal_s)
        self.add_callback(background_color_inner,[background_color_i], background_color_o.values())
        self.add_callback(label_color_inner,[label_color_i], [label_color_o])
        self.build()

    def update_preset(self, preset_name, mappings, *states):
        if preset_name is None:
            raise PreventUpdate()
        try:
            setter = getattr(self.visualiser, preset_name, None)
        except TypeError:
            raise PreventUpdate()
        states = states[0]
        modified_vals = setter()
        modified_vals = [m.__name__ for m in modified_vals]
        final_outputs = []
        for index, state in enumerate(states):
            is_modified = False
            states_possible_vals = list(mappings.items())[index][1]
            for mod in modified_vals:
                if mod in states_possible_vals:
                    final_outputs.append(mod)
                    is_modified = True
                    break
            if not is_modified:
                final_outputs.append(state)
        return final_outputs

    def update_graph(self, *args):
        if not isinstance(self.visualiser, TruthVisual):
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
            figure, legend = self.visualiser.build(graph_id=graph_id, legend=True)
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

    def export_modal(self, *args):
        changed_id = [p['prop_id']
                      for p in callback_context.triggered][0].split(".")[0]
        if changed_id == "":
            return False, []
        if export_modal_i["close_export"].component_id in changed_id:
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

    def docs_modal(self, n1, n2, is_open):
        if n1 or n2:
            return [not is_open]
        return [is_open]

    def info_modal(self, n1, n2, is_open):
        '''
        Node + Edge Count.
        Data table.
        Global information
        '''
        changed_id = [p['prop_id'] for p in callback_context.triggered][0]
        if info_modal_i["open_info"].component_id in changed_id:
            builder = self.visualiser._builder

            cards = self.create_heading_4("", "General Information")
            card = self.create_card("Node Count", len([*builder.view.nodes()]))
            card += self.create_card("Edge Count", len([*builder.view.edges()]))
            cards += self.create_cards("", card)
            cards += self.create_horizontal_row()

            cards += self.create_heading_4("", "Connectivity")
            card = self.create_card(
                "Node Connectivity", builder.view.node_connectivity())
            cards += self.create_cards("", card)
            cards += self.create_horizontal_row()

            cards += self.create_heading_4("", "Bipartite")
            card = self.create_card(
                "Is Bipartite", str(builder.view.is_bipartite()))
            cards += self.create_cards("", card)
            cards += self.create_horizontal_row()

            cards += self.create_heading_4("", "Components")
            c_str = [f'Is: {str(builder.view.is_strongly_connected())}',
                     f'Number: {str(builder.view.number_strongly_connected_components())}']
            card = self.create_card("Strongly Connected", c_str)
            c_str = [f'Is: {str(builder.view.is_weakly_connected())}',
                     f'Number: {str(builder.view.number_weakly_connected_components())}']
            card += self.create_card("Weakly Connected", c_str)
            c_str = [f'Is: {str(builder.view.is_attracting_component())}',
                     f'Number: {str(builder.view.number_attracting_components())}']
            card += self.create_card("Attracting Components", c_str)
            card += self.create_card("Is Biconnected",
                                     str(builder.view.is_biconnected()))
            cards += self.create_cards("", card)
            cards += self.create_horizontal_row()

            cards += self.create_heading_4("", "DAG")
            card = self.create_card(
                "Is Aperiodic", str(builder.view.is_aperiodic()))
            cards += self.create_cards("", card)
            cards += self.create_horizontal_row()

            cards += self.create_heading_4("", "Distance Measures")
            card = self.create_card("Diameter", builder.view.diameter())
            card += self.create_card("Radius", builder.view.radius())
            cards += self.create_cards("", card)
            cards += self.create_horizontal_row()

            cards += self.create_heading_4("", "Assortativity")
            card = self.create_card(
                "Degree Assortativity Coefficient", builder.view.degree_assortativity_coefficient())
            cards += self.create_cards("", card)
            cards += self.create_horizontal_row()

            cards += self.create_heading_4("", "Euler")
            card = self.create_card(
                "Is Eulerian", str(builder.view.is_eulerian()))
            card += self.create_card("Is Semi-Eulerian",
                                     str(builder.view.is_semieulerian()))
            cards += self.create_cards("", card)
            cards += self.create_horizontal_row()

            cards += self.create_heading_4("", "Tree")
            card = self.create_card("Is Tree", str(builder.view.is_tree()))
            card += self.create_card("Is Forest",
                                     str(builder.view.is_forest()))
            card += self.create_card("Is Arborescence",
                                     str(builder.view.is_arborescence()))
            card += self.create_card("Is Branching",
                                     str(builder.view.is_branching()))
            cards += self.create_cards("", card)
            cards += self.create_horizontal_row()

            cards += self.create_heading_4("", "Clustering")
            card = self.create_card("Triangles", builder.view.triangles())
            card += self.create_card("Transitivity",
                                     builder.view.transitivity())
            card += self.create_card("Average Clustering Coefficient",
                                     builder.view.average_clustering())
            cards += self.create_cards("", card)

            cards += self.create_heading_4("", "Asteroidal")
            card = self.create_card("AT Free", str(builder.view.is_at_free()))
            cards += self.create_cards("", card)
            cards += self.create_horizontal_row()

            cards += self.create_heading_4("", "Bridges")
            card = self.create_card(
                "Has Bridges", str(builder.view.has_bridges()))
            cards += self.create_cards("", card)
            cards += self.create_horizontal_row()

            cards += self.create_heading_4("", "Chordal")
            card = self.create_card(
                "Is Chordal", str(builder.view.is_chordal()))
            cards += self.create_cards("", card)
            cards += self.create_horizontal_row()

            cards += self.create_heading_4("", "Cliques")
            card = self.create_card("Number of Cliques", str(
                builder.view.graph_number_of_cliques()))
            cards += self.create_cards("", card)
            cards += self.create_horizontal_row()

            cards += self.create_heading_4("", "Node Information")
            n_cols, n_data, e_cols, e_data = self._generate_node_edge_tables(
                builder)
            cards += self.create_complex_table("", n_cols, n_data)
            cards += self.create_heading_4("", "Edge Information")
            cards += self.create_complex_table("", e_cols, e_data)

            return [True, cards]
        elif info_modal_i["close_info"].component_id in changed_id:
            return [hFalse, []]
        return [is_open, []]

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

    def man_modal(self, open, close, is_hidden):
        changed_id = [p['prop_id'] for p in callback_context.triggered][0]
        if man_tool_i["open_man"].component_id in changed_id:
            style = {'width': f'{str(65)}vw', 'height': f'{str(100)}vh'}
            is_hidden = hFalse
        else:
            style = {'width': f'{str(80)}vw', 'height': f'{str(100)}vh'}
            is_hidden = True
        return [is_hidden, style]

    def modify_nodes(self, t_remove, t_modify, elements, data):
        changed_id = [p['prop_id'] for p in callback_context.triggered][0]
        if not elements or not data:
            return [elements]

        if modify_node_i["t-remove"].component_id in changed_id:
            ids_to_remove = {ele_data['id'] for ele_data in data}
            [self.visualiser._builder.view.remove_node(
                int(d)) for d in ids_to_remove]
            new_elements = [
                ele for ele in elements if str(ele['data']['id']) not in ids_to_remove]
            return [new_elements]

        elif modify_node_i["t-modify"].component_id in changed_id:
            merging_node = data.pop(0)["id"]
            ids_to_merge = {ele_data['id'] for ele_data in data}
            self.visualiser._builder.view.merge_nodes(
                merging_node, ids_to_merge)
            new_elements = []
            for ele in elements:
                if str(ele["data"]["id"]) in ids_to_merge:
                    continue
                if "source" in ele["data"] or "target" in ele["data"]:
                    if str(ele["data"]["source"]) in ids_to_merge:
                        ele["data"]["source"] = merging_node
                        if "id" in ele["data"]:
                            del ele["data"]["id"]
                    if str(ele["data"]["target"]) in ids_to_merge:
                        ele["data"]["target"] = merging_node
                        if "id" in ele["data"]:
                            del ele["data"]["id"]
                    if (ele["data"]["source"] == merging_node
                            and ele["data"]["target"] == merging_node):
                        continue
                new_elements.append(ele)

            index = 0
            # When edges are still present but source or dest nodes are removed.
            nids = {str(ele_data["data"]['id'])
                    for ele_data in new_elements if "id" in ele_data["data"]}
            while index < len(new_elements):
                e = new_elements[index]
                if "source" in e["data"] or "target" in e["data"]:
                    if e["data"]["source"] not in nids:
                        del new_elements[index]
                    if e["data"]["target"] not in nids:
                        del new_elements[index]
                index += 1
            return [new_elements]
        return [elements]

    def advanced_modal(self, n1, n2, n3, is_open, form):
        c = []
        changed_id = [p['prop_id'] for p in callback_context.triggered][0]
        cur_layout = self.visualiser.layout
        if adv_modal_i["submit_adv"].component_id in changed_id:
            form = _derive_form(form)
            for k, v in form.items():
                cur_layout.add_param(k, v)
            return False, c, cur_layout.params
        if adv_modal_i["open_adv"].component_id in changed_id:
            cur_layout = self.visualiser.layout
            l_children = self.create_heading_3(
                '', f'Layout - {cur_layout.__class__.__name__}')
            for k, v in cur_layout.settings.items():
                if k in cur_layout.params.keys():
                    dv = cur_layout.params[k]
                else:
                    dv = None
                title = " ".join(re.findall(
                    '[A-Z][^A-Z]*', k[0].upper() + k[1:]))
                if v == int or v == float or v == str:
                    inp = self.create_input(k, dv)
                    title = title + f' - {v.__name__}'
                elif v == bool:
                    marks = {0: "False", 1: "True"}
                    inp = self.create_slider(k, 0, 1, dv, 1, marks)
                elif isinstance(v, list):
                    choices = [{"label": c, "value": c} for c in v]
                    inp = self.create_dropdown(k, choices, dv)
                else:
                    raise NotImplementedError()
                l_children += self.create_heading_6('', title)
                l_children += inp
                l_children += self.create_line_break(2)
            l_div = self.create_div("layout_settings", l_children)
            c = self.create_modal_body('adv_body', l_div)
            return True, c, cur_layout.params
        if adv_modal_i["close_adv"].component_id in changed_id:
            return False, c, cur_layout.params
        return is_open, c, cur_layout.params

    def background_color(self, color):
        if color is None:
            raise PreventUpdate()
        return [{"background-color": color["hex"]}, {"background-color": color["hex"]}]

    def label_color(self, color):
        if color is None:
            raise PreventUpdate()
        return [self.visualiser.stylesheet + [{"selector": "node", "style": {"color": color["hex"]}}]]

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
                               "set_design_names",
                               "get_load_predicates",
                               "get_loaded_design_names"]

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

    def _create_manual_toolbar(self):
        t_c = self.create_heading_5("temph", "Temporary Actions")
        t_c += self.create_button(
            modify_node_i["t-remove"].component_id, "Remove Selected Nodes")
        t_c += self.create_line_break(2)
        t_c += self.create_button(
            modify_node_i["t-modify"].component_id, "Merge Selected Nodes")
        children = self.create_div("temp", t_c)
        children += self.create_horizontal_row()

        p_c = self.create_heading_5("vis", "Visual")
        p_c += self.create_color_picker(
            background_color_i.component_id, "Background Color")
        p_c += self.create_line_break(2)
        p_c += self.create_color_picker(
            label_color_i.component_id, "Label Color")
        children += self.create_div("man_visual_div", p_c)
        children += self.create_horizontal_row()

        children += self.create_button(
            man_tool_i["close_man"].component_id, name="Close", className="export_img_button")
        return self.create_sidebar(man_tool_o["id"].component_id, "Manual Options",
                            children, className="col sidebar")


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
