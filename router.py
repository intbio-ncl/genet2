import os
import shutil
import uuid

from flask import Flask
from flask import session
from flask import render_template
from flask import redirect
from flask import send_from_directory
from flask import request
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from app.utility import forms
from app.utility import form_handlers
from app.utility.sbol_connector.connector import SBOLConnector
from app.converter.handler import file_convert
from app.converter.sbol_convert import export
from app.graph.world_graph import WorldGraph

from app.visualiser.design import DesignDash
from app.visualiser.editor import EditorDash
from app.visualiser.cypher import CypherDash
from app.visualiser.projection import ProjectionDash
from app.visualiser.truth import TruthDash

from app.validator.validator import Validator
from app.enhancer.enhancer import Enhancer

root_dir = "app"
static_dir = os.path.join(root_dir, "assets")
template_dir = os.path.join(root_dir, "templates")
sessions_dir = os.path.join(root_dir, "sessions")

server = Flask(__name__, static_folder=static_dir,
               template_folder=template_dir)

graph = WorldGraph()
design_dash = DesignDash(__name__, server, graph)
editor_dash = EditorDash(__name__, server, graph)
cypher_dash = CypherDash(__name__, server, graph)
projection_dash = ProjectionDash(__name__, server, graph)
truth_dash = TruthDash(__name__, server, graph)

design_dash.app.enable_dev_tools(debug=True)
cypher_dash.app.enable_dev_tools(debug=True)
projection_dash.app.enable_dev_tools(debug=True)
editor_dash.app.enable_dev_tools(debug=True)

app = DispatcherMiddleware(server, {
    design_dash.pathname: design_dash.app.server,
    cypher_dash.pathname: cypher_dash.app.server,
    projection_dash.pathname: projection_dash.app.server,
    editor_dash.pathname: editor_dash.app.server,
})
connector = SBOLConnector()
enhancer = Enhancer(graph)
validator = Validator(graph)

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
    export_graph = forms.add_export_graph_form(d_names)
    project_names = graph.driver.project.names()
    drop_projection = forms.add_remove_projection_form(project_names)
    add_graph_fn = None
    err_string = None
    success_str = None
    if "visual_filename" in session.keys():
        add_graph_fn = session["visual_filename"]
        g_name = session["graph_name"]
        ft = session["ft"]
    if upload_graph.validate_on_submit():
        add_graph_fn,g_name = form_handlers.handle_upload(upload_graph, session["session_dir"])
        ft = upload_graph.file_type.data
    elif paste_graph.validate_on_submit():
        add_graph_fn,g_name = form_handlers.handle_paste(paste_graph, session["session_dir"])
        ft = paste_graph.file_type.data
    elif sbh_graph.validate_on_submit():
        add_graph_fn,g_name = form_handlers.handle_synbiohub(sbh_graph, session["session_dir"], connector)
        if add_graph_fn is None:
            err_string = "Unable to find record."
        ft = "sbol"
    elif remove_graph.validate_on_submit():
        gn = remove_graph.graphs.data
        graph.remove_design(gn)
        d_names.remove(gn)
        remove_graph = forms.add_remove_graph_form(d_names)
        try:
            os.remove(os.path.join(session["session_dir"],gn+".xml"))
        except FileNotFoundError:
            pass
        success_str = f'{gn} Removed.'
    elif export_graph.validate_on_submit():
        out_dir = os.path.join(session["session_dir"], "designs")
        try:
            os.mkdir(out_dir)
        except FileExistsError:
            pass
        fn = export_graph.e_graphs.data+".xml"
        dfn = os.path.join(session["session_dir"],fn)
        export(dfn,[export_graph.e_graphs.data])
        shutil.copyfile(dfn, os.path.join(out_dir,fn))
        shutil.make_archive(out_dir, 'zip', out_dir)
        shutil.rmtree(out_dir)
        return send_from_directory(session["session_dir"], "designs.zip", as_attachment=True)
    elif drop_projection.validate_on_submit():
        dg = drop_projection.graphs.data
        if dg == "Remove All":
            for n in project_names:
                graph.driver.project.drop(n)
        else:
            graph.driver.project.drop(n)
    if add_graph_fn is not None:
        if g_name == "":
            g_name = add_graph_fn.split(os.path.sep)[-1].split(".")[0]
        return _add_graph(add_graph_fn, g_name,ft)

    return render_template('modify_graph.html', upload_graph=upload_graph,
                           paste_graph=paste_graph, sbh_graph=sbh_graph,
                           remove_graph=remove_graph, drop_projection=drop_projection,
                           export_graph=export_graph, err_string=err_string, success_str=success_str)


@server.route('/visualiser', methods=['GET', 'POST'])
def visualiser():
    return redirect(design_dash.pathname)


@server.route('/editor', methods=['GET', 'POST'])
def editor():
    return redirect(editor_dash.pathname)


@server.route('/cypher', methods=['GET', 'POST'])
def cypher():
    return redirect(cypher_dash.pathname)


@server.route('/gds', methods=['GET', 'POST'])
def gds():
    return redirect(projection_dash.pathname)


@server.route('/truth', methods=['GET', 'POST'])
def truth():
    return redirect(truth_dash.pathname)

@server.route('/evaluate', methods=['GET', 'POST'])
def evaluate():
    upload = forms.UploadDesignForm()
    d_names = graph.get_design_names()
    cg = forms.add_evaluate_graph_form(d_names)
    gn = None
    if request.method == "POST":
        if upload.validate_on_submit():
            ft = upload.file_type.data
            fn,gn = form_handlers.handle_upload(upload, session["session_dir"])
            gn = f'{session["uid"]}-{gn}'
            graph.remove_design(gn)
            file_convert(graph.driver,fn,gn,convert_type=ft)
        elif cg.validate_on_submit():
            gn = cg.graphs.data
        if gn is not None:
            feedback = enhancer.evaluate_design(gn, flatten=True)
            # Attach the descriptions here.
            descriptions = _get_evaluator_descriptions(feedback)
            return render_template("evaluate.html", feedback=feedback,
                                   descriptions=descriptions)

    return render_template("evaluate.html", upload=upload, cg=cg)


@server.route('/canonicalise', methods=['GET', 'POST'])
def canonicalise():
    upload = forms.UploadEnhanceDesignForm()
    d_names = graph.get_design_names()
    cg = forms.add_choose_graph_form(d_names)
    p_changes = None
    changes = None
    feedback = None
    gn = None
    if request.method == "POST":
        if "close" in request.form:
            return render_template("canonicalise.html", upload=upload, cg=cg)
        elif upload.validate_on_submit():
            gn, rm = _upload_graph(upload)
        elif cg.validate_on_submit():
            rm = cg.run_mode.data
            gn = cg.graphs.data

        if gn is not None:
            if upload.run_mode.data == "semi":
                p_changes, feedback = enhancer.canonicalise_graph(gn, mode=rm)
            elif upload.run_mode.data == "automated":
                changes, feedback = enhancer.canonicalise_graph(gn, mode=rm)

        if "submit_semi_canonicaliser" in request.form:
            replacements = {}
            for k, v in request.form.items():
                if k == "submit_semi_canonicaliser":
                    continue
                if v == "y":
                    old, new = k.split()
                    replacements[old] = new
                elif v != "none":
                    replacements[k] = v
            gn = session["c_gn"]
            changes = enhancer.apply_cannonical(replacements, gn)
            del session["c_gn"]
            del session["feedback"]

        if p_changes is not None:
            if len(p_changes) == 0:
                return render_template("canonicaliser.html", upload=upload, cg=cg, no_changes=True)
            changes = forms.add_semi_canonicaliser_form(p_changes)
            session["c_gn"] = gn
            session["feedback"] = feedback
            return render_template("canonicaliser.html", upload=upload, cg=cg, p_changes=changes, gn=gn)
        if changes is not None:
            if len(changes) == 0:
                return render_template("canonicaliser.html", upload=upload, cg=cg, no_changes=True)
            else:
                session["feedback"] = feedback
                return render_template("canonicaliser.html", upload=upload, cg=cg, s_changes=changes, gn=gn)

    return render_template("canonicaliser.html", upload=upload, cg=cg)


@server.route('/enhancement', methods=['GET', 'POST'])
def enhancement():
    d_names = graph.get_design_names()
    pipelines = ["all"] + enhancer.get_pipeline_names()
    upload = forms.add_enhance_graph_form(pipelines)
    cg = forms.add_choose_graph_enhancement_form(d_names, pipelines)
    p_changes = None
    changes = None
    feedback = None
    gn = None
    if request.method == "POST":
        if "close" in request.form:
            return render_template("enhancement.html", upload=upload, cg=cg)
        elif upload.validate_on_submit():
            gn, rm = _upload_graph(upload)
            pipeline = upload.pipelines.data
        elif cg.validate_on_submit():
            rm = cg.run_mode.data
            gn = cg.graphs.data
            pipeline = cg.pipelines.data
        if gn is not None:
            if pipeline == "all":
                pipeline = None
            else:
                pipeline = enhancer.cast_pipelines(pipelines)
            if upload.run_mode.data == "semi":
                p_changes, feedback = enhancer.enhance_design(
                    gn, mode=rm, pipeline=pipeline)
            elif upload.run_mode.data == "automated":
                changes, feedback = enhancer.enhance_design(
                    gn, mode=rm, pipeline=pipeline)

        if "submit_semi_enhancer" in request.form:
            replacements = {}
            for k, v in request.form.items():
                if k == "submit_semi_enhancer":
                    continue
                if v == "y":
                    old, new = k.split()
                    replacements[old] = new
                elif v != "none":
                    replacements[k] = v
            gn = session["c_gn"]
            changes = enhancer.apply_enhancement(replacements, gn)
            del session["c_gn"]
            del session["feedback"]

        if p_changes is not None:
            if len(p_changes) == 0:
                return render_template("enhancement.html", upload=upload, cg=cg, no_changes=True)
            changes = forms.add_semi_enhancer_form(p_changes)
            session["c_gn"] = gn
            session["feedback"] = feedback
            return render_template("enhancement.html", upload=upload, cg=cg, p_changes=changes, gn=gn)
        if changes is not None:
            if len(changes) == 0:
                return render_template("enhancement.html", upload=upload, cg=cg, no_changes=True)
            else:
                session["feedback"] = feedback
                return render_template("enhancement.html", upload=upload, cg=cg, s_changes=changes, gn=gn)
    return render_template("enhancement.html", upload=upload, cg=cg)


@server.route('/validation', methods=['GET', 'POST'])
def validation():
    upload = forms.UploadForm()
    use_graph = forms.SubmitForm()
    project_names = graph.get_projected_names()
    graph_name = forms.add_graph_name_form(project_names)

    if upload.validate_on_submit():
        fn,gn = form_handlers.handle_upload(
            upload, session["session_dir"], "sbol")
        gn = f'{session["uid"]}-{gn}'
        file_convert(graph.driver,fn,gn,convert_type="sbol")
        os.remove(fn)
        validator.validate(gn)
    if use_graph.validate_on_submit():
        pass
    if graph_name.validate_on_submit():
        pass
    return render_template("validation.html", upload=upload, use_graph=use_graph, graph_name=graph_name)

@server.route('/export_graph/<gn>', methods=['GET', 'POST'])
def export_graph(gn):
    out_dir = os.path.join(session["session_dir"], "designs")
    try:
        os.mkdir(out_dir)
    except FileExistsError:
        pass
    fn = gn + ".xml"
    dfn = os.path.join(session["session_dir"],fn)
    export(dfn,[gn])
    shutil.copyfile(dfn, os.path.join(out_dir,fn))
    shutil.make_archive(out_dir, 'zip', out_dir)
    shutil.rmtree(out_dir)
    return send_from_directory(session["session_dir"], "designs.zip", as_attachment=True)

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


def _upload_graph(upload):
    ft = upload.file_type.data
    fn,gn = form_handlers.handle_upload(upload, session["session_dir"])
    rm = upload.run_mode.data
    graph.remove_design(gn)
    file_convert(graph.driver,fn,gn,convert_type=ft)
    return gn, rm


def _add_graph(fn, g_name,ft):
    cf_true = forms.ConnectorFormTrue()
    cf_false = forms.ConnectorFormFalse()
    upload_graph = forms.UploadGraphForm()
    paste_graph = forms.PasteGraphForm()
    sbh_graph = forms.SynbioGraphForm()
    d_names = graph.get_design_names()
    remove_graph = forms.add_remove_graph_form(d_names)
    project_names = graph.driver.project.names()
    export_graph = forms.add_export_graph_form(["all"] + d_names)
    drop_projection = forms.add_remove_projection_form(project_names)
    if cf_true.cft_submit.data:
        orig_filename = fn
        dg = connector.connect(fn)
        fn = orig_filename.split("/")[-1].split(".")[0] + "_connected.xml"
        fn = os.path.join(session['session_dir'], fn)
        dg.save(fn, "xml")
        os.remove(orig_filename)
        del session["visual_filename"]
        del session["graph_name"]
        del session["ft"]

    elif cf_false.cff_submit.data:
        fn = session["visual_filename"]
        del session["visual_filename"]
        del session["graph_name"]
        del session["ft"]

    elif connector.can_connect(fn):
        session["ft"] = ft
        session["visual_filename"] = fn
        session["graph_name"] = g_name
        return render_template('modify_graph.html', upload_graph=upload_graph,
                               paste_graph=paste_graph, sbh_graph=sbh_graph, export_graph=export_graph,
                               drop_projection=drop_projection, remove_graph=remove_graph,
                               cf_true=cf_true, cf_false=cf_false)

    elif not os.path.isfile(fn):
        return render_template('modify_graph.html', upload_graph=upload_graph,
                               paste_graph=paste_graph, sbh_graph=sbh_graph, export_graph=export_graph,
                               drop_projection=drop_projection, remove_graph=remove_graph)

    file_convert(graph.driver,fn,g_name,convert_type=ft)
    return render_template('modify_graph.html', upload_graph=upload_graph,
                           paste_graph=paste_graph, sbh_graph=sbh_graph, export_graph=export_graph,
                           drop_projection=drop_projection, remove_graph=remove_graph, success_str="Graph Added.")


def _get_evaluator_descriptions(feedback):
    descriptions = {}
    evaluators = {k.__class__.__name__: k for k in enhancer.get_evaluators()}

    def ged(d):
        for k, v in d.items():
            desc = evaluators[k].__doc__ 
            if desc is None:
                desc = ""
            descriptions[k] = desc
            if "evaluators" in v:
                ged(v["evaluators"])
    ged(feedback["evaluators"])
    return descriptions
