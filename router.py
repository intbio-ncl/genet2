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

from app.graph.world_graph import WorldGraph

from app.visualiser.design import DesignDash
from app.visualiser.cypher import CypherDash
from app.visualiser.projection import ProjectionDash

root_dir = "app"
static_dir = os.path.join(root_dir, "assets")
template_dir = os.path.join(root_dir, "templates")
sessions_dir = os.path.join(root_dir, "sessions")

server = Flask(__name__, static_folder=static_dir,
               template_folder=template_dir)

graph = WorldGraph()
design_dash = DesignDash(__name__,server,graph)
cypher_dash = CypherDash(__name__,server,graph)
projection_dash = ProjectionDash(__name__,server,graph)

design_dash.app.enable_dev_tools(debug=True)
cypher_dash.app.enable_dev_tools(debug=True)
projection_dash.app.enable_dev_tools(debug=True)

app = DispatcherMiddleware(server, {
    design_dash.pathname : design_dash.app.server,
    cypher_dash.pathname: cypher_dash.app.server,
    #projection_dash.pathname: projection_dash.app.server
})
connector = SBOLConnector()
#enhancer = Enhancer(graph)
#validator = Validator(graph)

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
    d_names = graph.get_design_names()
    remove_graph = forms.add_remove_graph_form(d_names)
    project_names = graph.driver.project.names()
    drop_projection = forms.add_remove_projection_form(project_names)
    add_graph_fn = None
    err_string = None
    success_str = None
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
            sbh_graph, session["session_dir"], connector)
        mode = sbh_graph.mode.data
        g_name = sbh_graph.graph_name.data
        if add_graph_fn is None:
            err_string = "Unable to find record."
    elif remove_graph.validate_on_submit():
        graph.remove_design(remove_graph.graphs.data)
        d_names.remove(remove_graph.graphs.data)
        remove_graph = forms.add_remove_graph_form(d_names)
        success_str = f'{remove_graph.graphs.data} Removed.'
    elif drop_projection.validate_on_submit():
        dg = drop_projection.graphs.data
        if dg == "Remove All":
            for n in project_names:
                graph.driver.project.drop(n)
        else:
            graph.driver.project.drop(n)


    if add_graph_fn is not None:
        return _add_graph(add_graph_fn, mode, g_name)

    return render_template('modify_graph.html', upload_graph=upload_graph,
                           paste_graph=paste_graph, sbh_graph=sbh_graph,
                           remove_graph=remove_graph,drop_projection=drop_projection,
                           err_string=err_string,success_str=success_str)

@server.route('/visualiser', methods=['GET', 'POST'])
def visualiser():
    return redirect(design_dash.pathname)

@server.route('/cypher', methods=['GET', 'POST'])
def cypher():
    return redirect(cypher_dash.pathname)

@server.route('/gds', methods=['GET', 'POST'])
def gds():
    return redirect(projection_dash.pathname)

@server.route('/enhancement', methods=['GET', 'POST'])
def enhancement():
    upload = forms.UploadDesignForm()
    if upload.validate_on_submit():
        ft = upload.file_type.data
        fn = form_handlers.handle_upload(upload, session["session_dir"])
        gn = session['uid']
        mode = "duplicate"
        graph.add_graph(fn, mode=mode, name=gn,filetype=ft)
        os.remove(fn)
        enhancer.enhance(gn)

    return render_template("enhancement.html",upload=upload)

@server.route('/validation', methods=['GET', 'POST'])
def validation():
    upload = forms.UploadForm()
    use_graph = forms.SubmitForm()
    project_names = graph.project.get_projected_names()
    graph_name = forms.add_graph_name_form(project_names)

    if upload.validate_on_submit():
        fn = form_handlers.handle_upload(upload, session["session_dir"],"sbol")
        gn = session['uid']
        mode = "duplicate"
        graph.add_graph(fn, mode=mode, name=gn,filetype="sbol")
        os.remove(fn)
        validator.validate(gn)
    if use_graph.validate_on_submit():
        pass
    if graph_name.validate_on_submit():
        pass
    
    return render_template("validation.html",upload=upload,use_graph=use_graph,graph_name=graph_name)

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
    paste_graph = forms.PasteGraphForm()
    sbh_graph = forms.SynbioGraphForm()
    remove_graph = forms.add_remove_graph_form(graph.get_design_names())
    project_names = graph.driver.project.names()
    drop_projection = forms.add_remove_projection_form(project_names)
    if cf_true.cft_submit.data:
        orig_filename = fn
        dg = connector.connect(fn)
        fn = orig_filename.split("/")[-1].split(".")[0] + "_connected.xml"
        fn = os.path.join(session['session_dir'], fn)
        dg.save(fn, "xml")
        os.remove(orig_filename)
        del session["visual_filename"]
        del session["add_graph_mode"]
        del session["graph_name"]

    elif cf_false.cff_submit.data:
        fn = session["visual_filename"]
        del session["visual_filename"]
        del session["add_graph_mode"]
        del session["graph_name"]

    elif connector.can_connect(fn):
        session["visual_filename"] = fn
        session["add_graph_mode"] = mode
        session["graph_name"] = g_name
        return render_template('modify_graph.html', upload_graph=upload_graph,
                               paste_graph=paste_graph, sbh_graph=sbh_graph,
                               drop_projection=drop_projection, remove_graph=remove_graph,
                               cf_true=cf_true, cf_false=cf_false)

    elif not os.path.isfile(fn):
        return render_template('modify_graph.html', upload_graph=upload_graph,
                               paste_graph=paste_graph, sbh_graph=sbh_graph,
                               drop_projection=drop_projection, remove_graph=remove_graph)

    graph.add_design(fn,g_name,mode=mode)
    os.remove(fn)
    return render_template('modify_graph.html', upload_graph=upload_graph,
                           paste_graph=paste_graph, sbh_graph=sbh_graph,
                           drop_projection=drop_projection, remove_graph=remove_graph, success_str="Graph Added.")
