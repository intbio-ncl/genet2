from collections import OrderedDict

from dash.dependencies import Input, Output, State

id_prefix = "cyto"
graph_id = "full_graph"
default_options = []
preset_i = OrderedDict()
preset_o = OrderedDict()
update_i = OrderedDict()

not_modifier_identifiers = {"sidebar_id": "sidebar-left",
                            "utility_id": "utility"}

update_i_i = Input(graph_id, "style")
update_i_o = Output("load_i", "options")
load_i = Input("load_submit", "n_clicks")
load_s = {"gns" : State(update_i_o.component_id, "value"),
          "lp"  : State("lp", "value")}

load_o = Output("graph_content", "children")

update_o = {"graph_id": Output("content", "children"),
            "legend_id": Output("sidebar-right", "children")}

graph_type_o = {"id": Output("options", "style"),
                "div": Output("div", "children")}

docs_modal_i = {"open_doc": Input("open_doc", "n_clicks"),
                     "close_doc": Input("close_doc", "n_clicks")}
docs_modal_o = {"id": Output("doc_modal", "is_open")}
doc_modal_s = State("doc_modal", "is_open")

info_modal_i = {"open_info": Input("open_info", "n_clicks"),
                     "close_info": Input("close_info", "n_clicks")}
info_modal_o = {"id": Output("info_modal", "is_open"),
                      "info": Output("info_modal_form", "children")}
info_modal_s = State("info_modal", "is_open")

adv_modal_i = {"open_adv": Input("open_adv", "n_clicks"),
                    "close_adv": Input("close_adv", "n_clicks"),
                    "submit_adv": Input("submit_adv", "n_clicks")}
adv_modal_o = {"adv_modal_id": Output("adv_modal", "is_open"),
                     "form": Output("adv_modal_form", "children"),
                     "graph": Output(graph_id, "layout")}
adv_modal_s = [State("adv_modal", "is_open"),
                    State("adv_modal_form", "children")]
export_img_i = [Input("png", "n_clicks"),
                     Input("jpg", "n_clicks"),
                     Input("svg", "n_clicks")]
export_img_o = [Output(graph_id, "generateImage")]

export_map = []
export_modal_i = {"close_export": Input("close_export", "n_clicks")}
export_modal_o = {"id": Output("export_modal", "is_open"),
                        "data": Output("export_data", "children")}
export_modal_s = State("export_modal", "is_open")

man_tool_i = {"open_man": Input("open_man", "n_clicks"),
                   "close_man": Input("close_man", "n_clicks")}
man_tool_o = {"id": Output("man_toolbar", "hidden"),
                    "graph": Output(graph_id, "style")}
man_tool_s = State("man_toolbar", "hidden")

modify_node_i = {"t-remove": Input('t-remove-button', 'n_clicks'),
                      "t-modify": Input('t-modify-button', 'n_clicks')}
modify_node_o = [Output(graph_id, 'elements')]
modify_node_s = [State(graph_id, 'elements'),
                      State(graph_id, 'selectedNodeData')]

background_color_i = Input('background-picker', 'value')
background_color_o = {"graph": Output("content", "style"),
                            "legend": Output("sidebar-right", "style")}

label_color_i = Input('label-picker', 'value')
label_color_o = Output(graph_id, "stylesheet")

cypher_i = {"submit": Input("submit_cypher", "n_clicks")}
cypher_o = {"graph_id": Output("graph_content", "children"),
                 "datatable_id": Output("datatable", "children")}
cypher_s = State("query", "value")


project_load_i = Input("project_load_i", "value")
project_load_o = {"graph_id": Output("graph_content", "children"),
                       "datatable": Output("datatable", "children"),
                       "info": Output("info", "children"),
                       "procs": Output("procedures", "style")}
plo_i_box = []
project_params_i = Input("preset_graph", "value")
project_params_o = Output("preset_params","children")

project_i = {"raw_submit": Input("raw_submit", "n_clicks"),
               "preset_submit": Input("preset_submit", "n_clicks"),
               "native_submit": Input("native_submit", "n_clicks")}

project_o = {"vis_i": Output(project_load_i.component_id, "options"),
               "message": Output("project_message", "children")}
project_s = {"raw_i": State("raw_i", "value"),
             "gn_r" : State("gn_r","value"),
             "native_name": State("native_name", "value"),
             "node": State("node", "value"),
             "edge": State("edge", "value"),
             "node_properties": State("node_propertie", "value"),
             "edge_properties": State("edge_propertie", "value"),
             "gn_n" : State("gn_n","value"),
             "preset_name": State("preset_name", "value"),
             "preset_graph": State(project_params_i.component_id, "value"),
             "preset_params" : State(project_params_o.component_id,"children"),
             "gn_p" : State("gn_p","value"),}


procedure_i = []
procedure_s = []
procedure_o = [Output("procedure_table", "children")]
