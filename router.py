import os
import uuid

from flask import Flask
from flask import session
from flask import render_template
from flask import redirect
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from app.utility import forms
from app.utility import form_handlers
from app.utility.sbol_connector.connector import SBOLConnector
from app.graphs.neo_graph.nv_graph import NVGraph
from app.dashboards.design import DesignDash

root_dir = "app"
static_dir = 'assets'
template_dir = os.path.join(root_dir, "templates")
sessions_dir = os.path.join(root_dir, "sessions")

server = Flask(__name__, static_folder=static_dir,
               template_folder=template_dir)
design_graph = NVGraph()
design_dash = DesignDash(__name__,server,design_graph)
design_dash.app.enable_dev_tools(debug=True)
app = DispatcherMiddleware(server, {
    design_dash.pathname : design_dash.app.server,
})
sbol_connector = SBOLConnector()

server.config['SESSION_PERMANENT'] = True
server.config['SESSION_TYPE'] = 'filesystem'
server.config['SESSION_FILE_THRESHOLD'] = 100
server.config['SECRET_KEY'] = "Secret"
server.config['SESSION_FILE_DIR'] = os.path.join(root_dir, "flask_sessions")


@server.route('/', methods=['GET', 'POST'])
@server.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@server.route('/modify-graph', methods=['GET', 'POST'])
def modify_graph():
    upload_graph = forms.UploadGraphForm()
    paste_graph = forms.PasteGraphForm()
    sbh_graph = forms.SynbioGraphForm()
    purge_graph = forms.PurgeGraphForm()
    remove_graph = forms.add_remove_graph_form(design_graph.get_graph_names())
    add_graph_fn = None
    err_string = None
    if "visual_filename" in session.keys():
        add_graph_fn = session["visual_filename"]
        mode = session["add_graph_mode"]
        g_name = session["graph_name"]
    if upload_graph.validate_on_submit():
        add_graph_fn = form_handlers.handle_upload(
            upload_graph, session["session_dir"])
        mode = upload_graph.mode.data
        g_name = upload_graph.graph_name.data
    elif paste_graph.validate_on_submit():
        add_graph_fn = form_handlers.handle_paste(
            paste_graph, session["session_dir"])
        mode = paste_graph.mode.data
        g_name = paste_graph.graph_name.data
    elif sbh_graph.validate_on_submit():
        add_graph_fn = form_handlers.handle_synbiohub(
            sbh_graph, session["session_dir"], sbol_connector)
        mode = sbh_graph.mode.data
        g_name = sbh_graph.graph_name.data
        if add_graph_fn is None:
            err_string = "Unable to find record."
    elif purge_graph.validate_on_submit():
        design_graph.purge()
    elif remove_graph.validate_on_submit():
        design_graph.remove_graph(remove_graph.graphs.data)


    if add_graph_fn is not None:
        return _add_graph(add_graph_fn, mode, g_name)

    return render_template('modify_graph.html', upload_graph=upload_graph,
                           paste_graph=paste_graph, sbh_graph=sbh_graph,
                           purge_graph=purge_graph, remove_graph=remove_graph,
                           err_string=err_string)

@server.route('/visualiser', methods=['GET', 'POST'])
def visualiser():
    return redirect(design_dash.pathname)

@server.before_request
def before_request_func():
    if session.get("uid") is None:
        session['uid'] = str(uuid.uuid4())
    if session.get("session_dir") is None:
        session['session_dir'] = os.path.join(sessions_dir, session['uid'])
    try:
        os.makedirs(os.path.join(sessions_dir, session['uid']))
    except FileExistsError:
        pass

def _add_graph(fn, mode, g_name):
    cf_true = forms.ConnectorFormTrue()
    cf_false = forms.ConnectorFormFalse()
    upload_graph = forms.UploadGraphForm()
    purge_graph = forms.PurgeGraphForm()
    paste_graph = forms.PasteGraphForm()
    sbh_graph = forms.SynbioGraphForm()
    remove_graph = forms.add_remove_graph_form(design_graph.get_graph_names())
    if cf_true.cft_submit.data:
        orig_filename = fn
        graph = sbol_connector.connect(fn)
        fn = orig_filename.split("/")[-1].split(".")[0] + "_connected.xml"
        fn = os.path.join(session['session_dir'], fn)
        graph.save(fn, "sbolxml")
        os.remove(orig_filename)
        del session["visual_filename"]
        del session["add_graph_mode"]
        del session["graph_name"]

    elif cf_false.cff_submit.data:
        fn = session["visual_filename"]
        del session["visual_filename"]
        del session["add_graph_mode"]
        del session["graph_name"]

    elif sbol_connector.can_connect(fn):
        session["visual_filename"] = fn
        session["add_graph_mode"] = mode
        return render_template('modify_graph.html', upload_graph=upload_graph,
                               paste_graph=paste_graph, sbh_graph=sbh_graph,
                               purge_graph=purge_graph, remove_graph=remove_graph,
                               cf_true=cf_true, cf_false=cf_false)

    elif not os.path.isfile(fn):
        return render_template('modify_graph.html', upload_graph=upload_graph,
                               paste_graph=paste_graph, sbh_graph=sbh_graph,
                               purge_graph=purge_graph, remove_graph=remove_graph)

    design_graph.add_graph(fn, mode=mode, name=g_name)
    os.remove(fn)
    return render_template('modify_graph.html', upload_graph=upload_graph,
                           paste_graph=paste_graph, sbh_graph=sbh_graph,
                           purge_graph=purge_graph, remove_graph=remove_graph, success=True)
