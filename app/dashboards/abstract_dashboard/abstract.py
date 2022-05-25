
import dash
from dash import dcc
import dash_bootstrap_components as dbc
from dash import html
import dash_daq as daq
import dash_bio as dashbio
from dash import dash_table

external_scripts = [
    {
        'src': 'https://code.jquery.com/jquery-3.4.1.js',
        'integrity': 'sha256-WpOohJOqMqqyKL9FccASB9O0KwACQJpFTUBLTYOVvVU=',
        'crossorigin': 'anonymous'
    },

    {
        'src': 'https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js',
        'integrity': 'sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo',
        'crossorigin': 'anonymous'
    },

    {
        'src': 'https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js',
        'integrity': 'sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6',
        'crossorigin': 'anonymous'
    },
]

style_sheet = [
    {
        'rel': 'stylesheet',
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css',
        'integrity': 'sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh',
        'crossorigin': 'anonymous'
    }
]


class AbstractDash:
    def __init__(self, graph_visualiser, name, server, pathname, **kwargs):
        self.app = dash.Dash(name, server=server, url_base_pathname=pathname,
                             external_stylesheets=style_sheet, external_scripts=external_scripts, **kwargs)
        self.pathname = pathname
        self.visualiser = graph_visualiser
        self.children = []
        self.parameters_calls = []
        self.callbacks = {}

    def build(self):
        for k, v in self.callbacks.items():
            if v["states"] == []:
                self.app.callback(v["outputs"], v["inputs"])(k)
            else:
                self.app.callback(v["outputs"], v["inputs"], v["states"])(k)

    def add_callback(self, function, inputs, outputs, states=None):
        if states is None:
            states = []
        self.callbacks[function] = {
            "inputs": inputs, "outputs": outputs, "states": states}

    def replace(self, div):
        for index, element in enumerate(self.children):
            if div.id == element.id:
                self.children.pop(index)
                self.children.insert(index, div)
                break
        else:
            self.children.append(div)

    def _create_element(self, *elements):
        self.children = self.children + [*elements]
        return elements

    def create_heading_1(self, identifier, children, add=False, **kwargs):
        heading = html.H1(id=identifier, children=children, **kwargs)
        if add:
            return self._create_element(heading)
        else:
            return [heading]

    def create_heading_2(self, identifier, children, add=False, **kwargs):
        heading = html.H2(id=identifier, children=children, **kwargs)
        if add:
            return self._create_element(heading)
        else:
            return [heading]

    def create_heading_3(self, identifier, children, add=False, **kwargs):
        heading = html.H3(id=identifier, children=children, **kwargs)
        if add:
            return self._create_element(heading)
        else:
            return [heading]

    def create_heading_4(self, identifier, children, add=False, **kwargs):
        heading = html.H4(id=identifier, children=children, **kwargs)
        if add:
            return self._create_element(heading)
        else:
            return [heading]

    def create_heading_5(self, identifier, children, add=False, **kwargs):
        heading = html.H5(id=identifier, children=children, **kwargs)
        if add:
            return self._create_element(heading)
        else:
            return [heading]

    def create_heading_6(self, identifier, children, add=False, **kwargs):
        heading = html.H6(id=identifier, children=children, **kwargs)
        if add:
            return self._create_element(heading)
        else:
            return [heading]

    def create_div(self, identifier, text, add=False, **kwargs):
        div = html.Div(id=identifier, children=text, **kwargs)
        if add:
            return self._create_element(div)
        else:
            return [div]

    def create_button(self, identifier, name=None, href=None, add=False, **kwargs):
        if href is None:
            if not name:
                name = identifier
            button = html.Button(name, id=identifier, **kwargs)
        else:
            button = html.A(html.Button(identifier), href="/" +
                            href, target="_blank", **kwargs)
        if add:
            return self._create_element(button)
        else:
            return [button]

    def create_input(self, identifier, value=None, add=False, **kwargs):
        if value is None:
            value = ""
        input_l = dcc.Input(id=identifier, value=value, **kwargs)
        if add:
            return self._create_element(input_l)
        else:
            return [input_l]

    def create_i(self, identifier, add=False, **kwargs):
        input_l = html.I(id=identifier, **kwargs)
        if add:
            return self._create_element(input_l)
        else:
            return [input_l]

    def create_span(self, identifier, children, add=False, **kwargs):
        input_l = html.Span(id=identifier, children=children, **kwargs)
        if add:
            return self._create_element(input_l)
        else:
            return [input_l]

    def create_dropdown(self, identifier, options, value=None, add=False, **kwargs):
        dropdown = dcc.Dropdown(
            id=identifier, options=options, value=value,**kwargs)
        if add:
            return self._create_element(dropdown)
        else:
            return [dropdown]

    def create_radio_item(self, identifier, options, value=None, add=False, **kwargs):
        radio = dcc.RadioItems(
            id=identifier, options=options, value=value, **kwargs)
        if add:
            return self._create_element(radio)
        else:
            return [radio]

    def create_checklist(self, identifier, name, options, add=False, **kwargs):
        checklist = dcc.Checklist(id=identifier, options=options, **kwargs)
        if name is not None:
            label = html.Label(name)
            if add:
                return self._create_element(label, checklist)
            else:
                return [label, checklist]
        else:
            if add:
                return self._create_element(checklist)
            else:
                return [checklist]

    def create_slider(self, identifier, min_val, max_val, default_val=None, step=None, marks=None, add=False, **kwargs):
        if default_val is None:
            default_val = max_val/2
        if marks is None:
            marks = {}
            marks[min_val] = str(int(min_val))
            marks[max_val] = str(int(max_val))
        if step is None:
            step = max_val/4
        slider = dcc.Slider(id=identifier, min=min_val, max=max_val,
                            value=default_val, marks=marks, step=step, **kwargs)
        if add:
            return self._create_element(slider)
        else:
            return [slider]

    def create_sidebar(self, id, name, content, add=False, **kwagrs):
        children = [html.H2(name, className="display"), *content]
        sidebar = html.Div(id=id, children=children, **kwagrs)
        if add:
            return self._create_element(sidebar)
        else:
            return [sidebar]

    def create_horizontal_row(self, add=False):
        if add:
            return self._create_element(html.Hr())
        else:
            return [html.Hr()]

    def add_table(self, identifier, children, add=False, **kwargs):
        table = html.Table(id=identifier, children=children, **kwargs)
        if add:
            return self._create_element(table)
        else:
            return [table]

    def add_tr(self, identifier, children, add=False, **kwargs):
        tr = html.Tr(id=identifier, children=children, **kwargs)
        if add:
            return self._create_element(tr)
        else:
            return [tr]

    def add_th(self, identifier, children, add=False, **kwargs):
        th = html.Th(id=identifier, children=children, **kwargs)
        if add:
            return self._create_element(th)
        else:
            return [th]

    def add_td(self, identifier, children, add=False, **kwargs):
        th = html.Td(id=identifier, children=children, **kwargs)
        if add:
            return self._create_element(th)
        else:
            return [th]

    def create_line_break(self, number=1, add=False):
        if add:
            for n in number:
                self._create_element(html.Br())
            return self.children
        else:
            return [html.Br()] * number

    def create_alert(self, identifier, text, add=False, **kwargs):
        alert = dbc.Alert(id=identifier, children=text, **kwargs)
        if add:
            return self._create_element(alert)
        else:
            return [alert]

    def create_toggle_switch(self, identifier, name, value=False, add=False, **kwargs):
        switch = daq.ToggleSwitch(
            id=identifier, label=name, value=value, **kwargs)
        if add:
            return self._create_element(switch)
        else:
            return [switch]

    def create_color_picker(self, identifier, name, add=False, **kwargs):
        picker = daq.ColorPicker(id=identifier, label=name, **kwargs)
        if add:
            return self._create_element(picker)
        else:
            return [picker]

    def create_indicator(self, identifier, name, color="green", add=False, **kwargs):
        indicator = daq.Indicator(
            id=identifier, label=name, color=color, **kwargs)
        if add:
            return self._create_element(indicator)
        else:
            return [indicator]

    def create_numeric_input(self, identifier, name, min_val, max_val, default_val=None, add=False, **kwargs):
        if default_val is None:
            default_val = max_val/2

        label = html.Label(name)
        num_input = daq.NumericInput(
            id=identifier, min=min_val, max=max_val, value=default_val, **kwargs)
        if add:
            return self._create_element(label, num_input)
        else:
            return [label, num_input]

    def create_file_upload(self, identifier, name, graph_parent_id, add=False, **kwargs):
        upload_box = dcc.Upload(id=identifier, children=html.Div(
            [dbc.Button(name, color="secondary", className="mr-1")]), multiple=True, **kwargs)
        if add:
            return self._create_element(upload_box)
        else:
            return [upload_box]

    def create_accordion(self, identifier, cards, add=False, **kwargs):
        f_cards = []
        for index, (name, value) in enumerate(cards):
            id_index = identifier + str(index)
            c = html.Button(children=name, id="", 
            className="btn btn-link", type="button", **{
                      "data-toggle": "collapse", 
                      "data-target": f"#collapse{id_index}",
                      "aria-expanded": "false", 
                      "aria-controls": f"collapse{id_index}"})

            c = self.create_heading_5(name+"_h", c, className="mb-0")
            c = self.create_div(
                f"heading{id_index}", c, className="card-header")

            b = self.create_div(name+"_c_b", value, className="card-body")
            b = self.create_div(f'collapse{id_index}', b, **{"className": "collapse",
                                "aria-labelledby": f"heading{id_index}", "data-parent": f"#{identifier}"})
            card = self.create_div(name+"_c", c+b, className="card")
            f_cards += (card)

        acc = self.create_div(identifier, f_cards,
                              className="accordion", **kwargs)
        if add:
            return self._create_element(acc)
        else:
            return acc

    def add_sequence_viewer(self, identifier, sequence, add=False, **kwargs):
        sequence_box = dashbio.SequenceViewer(
            id=identifier, sequence=sequence, **kwargs)
        if add:
            return self._create_element(sequence_box)
        else:
            return [sequence_box]

    def create_complex_table(self, identifier, columns, data, add=False, **kwargs):
        table = dash_table.DataTable(
            id=identifier,
            columns=columns,
            data=data,
            editable=True,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            column_selectable="single",
            row_selectable="multi",
            row_deletable=True,
            selected_columns=[],
            selected_rows=[],
            page_action="native",
            page_current=0,
            page_size=20,
            style_cell={'textAlign': 'left'},
            style_table={'overflowX': 'auto'})
        if add:
            return self._create_element(table)
        else:
            return [table]

    def create_hyperlink(self, identifier, href, add=False):
        a_tag = html.A(identifier, href=href)
        if add:
            return self._create_element(a_tag)
        else:
            return [a_tag]

    def create_paragraph(self, text, add=False, **kwargs):
        p_tag = html.P(text, **kwargs)
        if add:
            return self._create_element(p_tag)
        else:
            return [p_tag]

    def create_detail(self, identifier, children, add=False, **kwargs):
        detail_tag = html.Details(id=identifier, children=children, **kwargs)
        if add:
            return self._create_element(detail_tag)
        else:
            return [detail_tag]

    def create_summary(self, identifier, text, add=False, **kwargs):
        sum_tag = html.Summary(id=identifier, children=text, **kwargs)
        if add:
            return self._create_element(sum_tag)
        else:
            return [sum_tag]

    def create_modal(self, identifier, close_identifier, name, contents, submit_button=None, add=False, **kwargs):
        modal_header = dbc.ModalHeader(name)
        modal_body = dbc.ModalBody(contents)
        if submit_button is not None:
            submit_button = [dbc.Button(
                "Submit", id=submit_button, className="ml-auto")]
        else:
            submit_button = []
        modal_footer = dbc.ModalFooter(
            submit_button + [dbc.Button("Close", id=close_identifier, className="ml-auto")])
        modal = dbc.Modal(id=identifier, children=[
                          modal_header, modal_body, modal_footer], size="xl", **kwargs)
        if add:
            return self._create_element(modal)
        else:
            return [modal]

    def create_modal_body(self, identifiers, contents, add=False, **kwargs):
        modal_body = dbc.ModalBody(contents, id=identifiers)
        if add:
            return self._create_element(modal_body)
        else:
            return [modal_body]

    def create_question_mark(self, identifier, add=False, **kwargs):
        q_mark = html.Abbr(id=identifier, children="\uFE56",
                           className="help-tip")
        if add:
            return self._create_element(q_mark)
        else:
            return [q_mark]

    def create_legend(self, legend_dict, add=False, **kwargs):
        legend_body = []
        for name, legend_items in legend_dict.items():
            l_children = self.create_heading_5(name, name)
            for item_name, item_val in legend_items.items():
                style = {"background": item_val}
                l_children.append(
                    html.Li(children=[html.Span(style=style), html.P(item_name)]))
            legend_body.append(
                html.Ul(children=l_children, className="legend-labels"))

        legend_body_div = self.create_div(
            "legend_body", legend_body, className="legend-scale")
        if add:
            return self.create_div("sb", legend_body_div, add=True, className="graph-legend")
        else:
            return self.create_div("sb", legend_body_div, className="graph-legend")

    def create_text_area(self, identifier, add=False, **kwargs):
        ta = dcc.Textarea(id=identifier, style={
                          'width': '100%', 'height': 500}, **kwargs)
        if add:
            return self._create_element(ta)
        else:
            return [ta]

    def create_card(self, heading, body, add=False, **kwargs):
        if not isinstance(body, list):
            body = [body]
        heading = self.create_heading_5("", heading)
        card_heading = self.create_div("", heading, className="card-header")
        body_l = []
        for b in body:
            body_l += self.create_paragraph(b)
        card_body = self.create_div("", body_l, className="card-body")
        col = self.create_div("", card_heading + card_body, className="col-md")
        if add:
            return self._create_element(col)
        else:
            return col

    def create_cards(self, identifier, cards, add=False, **kwargs):
        card_range = self.create_div(identifier, cards, className="row")
        if add:
            return self._create_element(card_range)
        else:
            return card_range
