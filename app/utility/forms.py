from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms import TextAreaField
from wtforms import SelectField
from wtforms import BooleanField
from wtforms import FileField
from wtforms import validators
from wtforms import FormField
from wtforms.form import BaseForm
graph_choices = [('SBOL', 'SBOL'), ("GBK", "Genbank")]
r_mode = [("automated", "Automated"), ("semi", "Semi-Automated")]

class SubmitForm(FlaskForm):
    class Meta:
        csrf = False
    submit = SubmitField('Submit')


class UploadForm(FlaskForm):
    class Meta:
        csrf = False
    submit_upload = SubmitField('Submit')
    upload = FileField('Upload File', validators=[validators.InputRequired()])

class EnhanceTruthGraphForm(FlaskForm):
    class Meta:
        csrf = False
    enhance_submit = SubmitField('Run Enhancement')


class PasteForm(FlaskForm):
    class Meta:
        csrf = False
    submit_paste = SubmitField('Submit')
    paste = TextAreaField('Paste', validators=[validators.InputRequired()])


class UploadDesignForm(UploadForm):
    class Meta:
        csrf = False
    file_type = SelectField("Datatype", choices=graph_choices)

class UploadEnhanceDesignForm(UploadDesignForm):
    class Meta:
        csrf = False
    run_mode = SelectField("Run Mode", choices=r_mode)

class UploadGraphForm(UploadDesignForm):
    class Meta:
        csrf = False
    graph_name = TextAreaField('Graph Name (Optional)')

class PasteGraphForm(PasteForm):
    class Meta:
        csrf = False
    file_type = SelectField("Datatype", choices=graph_choices)
    graph_name = TextAreaField('Graph Name (Optional)')


class SynbioGraphForm(FlaskForm):
    class Meta:
        csrf = False
    submit_sbh = SubmitField('Submit')
    pmid = TextAreaField('ID', validators=[validators.InputRequired()])
    graph_name = TextAreaField('Graph Name (Optional)')


class PurgeGraphForm(FlaskForm):
    purge_graph = SubmitField('Reset Graph')


class ConnectorFormTrue(FlaskForm):
    class Meta:
        csrf = False
    cft_submit = SubmitField('Yes')


class ConnectorFormFalse(FlaskForm):
    class Meta:
        csrf = False
    cff_submit = SubmitField('No')


def add_remove_graph_form(choices, **kwargs):
    class RemoveGraphForm(FlaskForm):
        class Meta:
            csrf = False
        submit = SubmitField('Remove')
    setattr(RemoveGraphForm, "graphs", SelectField(
        "Graph Name", choices=[(c, c) for c in choices]))
    return RemoveGraphForm(**kwargs)

def add_evaluate_graph_form(choices, **kwargs):
    class EvalGraphForm(FlaskForm):
        class Meta:
            csrf = False
        submit = SubmitField('Submit')
    setattr(EvalGraphForm, "graphs", SelectField(
        "Graph Name", choices=[(c, c) for c in choices]))
    return EvalGraphForm(**kwargs)

def add_choose_graph_form(choices, **kwargs):
    class ChooseGraphForm(FlaskForm):
        class Meta:
            csrf = False
        submit = SubmitField('Submit')
        run_mode = SelectField("Run Mode", choices=r_mode)
    setattr(ChooseGraphForm, "graphs", SelectField(
        "Graph Name", choices=[(c, c) for c in choices]))
    return ChooseGraphForm(**kwargs)


def add_export_graph_form(choices, **kwargs):
    class ExportGraphForm(FlaskForm):
        class Meta:
            csrf = False
        export = SubmitField('Export')
    setattr(ExportGraphForm, "e_graphs", SelectField(
        "Graph Name", choices=[(c, c) for c in choices]))
    return ExportGraphForm(**kwargs)


def add_remove_projection_form(choices, **kwargs):
    class RemoveProjectionForm(FlaskForm):
        class Meta:
            csrf = False
        submit = SubmitField('Remove')
    choices = ["Remove All"] + choices
    setattr(RemoveProjectionForm, "graphs", SelectField(
        "Projection Name", choices=[(c, c) for c in choices]))
    return RemoveProjectionForm(**kwargs)


def add_graph_name_form(choices, **kwargs):
    class ExportGraphForm(FlaskForm):
        class Meta:
            csrf = False
        submit = SubmitField('Submit')
    setattr(ExportGraphForm, "graphs", SelectField(
        "Graph Name", choices=[(c, c) for c in choices]))
    return ExportGraphForm(**kwargs)

def form_from_fields(fields):
    def create_form(**kwargs):
        form = BaseForm(fields)
        form.process(**kwargs)
        return form
    return create_form

def add_semi_canonicaliser_form(choices, **kwargs):
    class SemiCanonicaliserGraphForm(FlaskForm):
        class Meta:
            csrf = False
        submit_semi_canonicaliser = SubmitField('Submit')
        close = SubmitField("Cancel")
    fields = []
    for k,v in choices.items():
        data = {"label":k,"description":v}
        if isinstance(v,dict):
            identifier = k
            data["description"] = "Choice"
            data["choices"] = [("none","none")]+[(s,f'{s} - {c}% Confidence') for s,c in v.items()]
            fields.append((identifier,SelectField,data))
        else:
            identifier = f'{k} {v}'
            fields.append((identifier,BooleanField,data))
    stage_form = form_from_fields([(field_id,f_type(**data)) for field_id,f_type,data in fields])
    setattr(SemiCanonicaliserGraphForm, "forms",FormField(stage_form))
    return SemiCanonicaliserGraphForm(**kwargs)

def add_enhance_graph_form(pipelines,**kwargs):
    class UploadEnhanceDesignPipelineForm(UploadEnhanceDesignForm):
        class Meta:
            csrf = False
    setattr(UploadEnhanceDesignPipelineForm, "pipelines", SelectField(
        "Enhancement Factor", choices=[(c, c) for c in pipelines]))
    return UploadEnhanceDesignPipelineForm(**kwargs)

def add_choose_graph_enhancement_form(choices,pipelines, **kwargs):
    class ChooseGraphForm(FlaskForm):
        class Meta:
            csrf = False
        submit = SubmitField('Submit')
        run_mode = SelectField("Run Mode", choices=r_mode)
    setattr(ChooseGraphForm, "graphs", SelectField(
        "Graph Name", choices=[(c, c) for c in choices]))
    setattr(ChooseGraphForm, "pipelines", SelectField(
        "Enhancement Factor", choices=[(c, c) for c in pipelines]))
    return ChooseGraphForm(**kwargs)