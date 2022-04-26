from collections import OrderedDict

from dash.dependencies import Input, Output, State

id_prefix = "cyto"
graph_id = "full_graph"
default_options = []
preset_inputs = OrderedDict()
preset_outputs = OrderedDict()
update_inputs = OrderedDict()

not_modifier_identifiers = {"sidebar_id": "sidebar-left",
                            "utility_id": "utility"}

update_outputs = {"graph_id": Output("content", "children"),
                  "legend_id": Output("sidebar-right", "children")}

graph_type_outputs = {"id": Output("options", "style"),
                      "div": Output("div", "children")}

docs_modal_inputs = {"open_doc": Input("open_doc", "n_clicks"),
                     "close_doc": Input("close_doc", "n_clicks")}
docs_modal_outputs = {"id": Output("doc_modal", "is_open")}
doc_modal_states = State("doc_modal", "is_open")

info_modal_inputs = {"open_info": Input("open_info", "n_clicks"),
                     "close_info": Input("close_info", "n_clicks")}
info_modal_outputs = {"id": Output("info_modal", "is_open"),
                      "info": Output("info_modal_form", "children")}
info_modal_states = State("info_modal", "is_open")

adv_modal_inputs = {"open_adv": Input("open_adv", "n_clicks"),
                    "close_adv": Input("close_adv", "n_clicks"),
                    "submit_adv": Input("submit_adv", "n_clicks")}
adv_modal_outputs = {"adv_modal_id": Output("adv_modal", "is_open"),
                     "form": Output("adv_modal_form", "children"),
                     "graph": Output(graph_id, "layout")}
adv_modal_states = [State("adv_modal", "is_open"),
                    State("adv_modal_form", "children")]
export_img_inputs = [Input("png", "n_clicks"),
                     Input("jpg", "n_clicks"),
                     Input("svg", "n_clicks")]
export_img_outputs = Output(graph_id, "generateImage")

export_map = []
export_modal_inputs = {"close_export": Input("close_export", "n_clicks")}
export_modal_outputs = {"id": Output("export_modal", "is_open"),
                        "data": Output("export_data", "children")}
export_modal_states = State("export_modal", "is_open")

man_tool_inputs = {"open_man": Input("open_man", "n_clicks"),
                   "close_man": Input("close_man", "n_clicks")}
man_tool_outputs = {"id": Output("man_toolbar", "hidden"),
                    "graph": Output(graph_id, "style")}
man_tool_states = State("man_toolbar", "hidden")

modify_node_inputs = {"t-remove": Input('t-remove-button', 'n_clicks'),
                    "t-modify": Input('t-modify-button', 'n_clicks')}
modify_node_outputs = [Output(graph_id, 'elements')]
modify_node_states = [State(graph_id, 'elements'),
                      State(graph_id, 'selectedNodeData')]

background_color_input = Input('background-picker', 'value')
background_color_outputs = {"graph": Output("content", "style"),
                            "legend": Output("sidebar-right", "style")}

label_color_input = Input('label-picker', 'value')
label_color_output = Output(graph_id, "stylesheet")

cypher_input = {"submit": Input("submit_cypher", "n_clicks")}
cypher_output = {"graph_id": Output("graph_content", "children"),
                 "datatable_id": Output("datatable","children")}
cypher_state = State("query", "value")