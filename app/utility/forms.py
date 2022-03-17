from flask_wtf import FlaskForm
from wtforms import SubmitField 
from wtforms import TextAreaField 
from wtforms import SelectField
from wtforms import FileField 
from wtforms import validators

graph_choices = [('SBOL', 'SBOL')]
mode_choices = [('ignore','Ignore (Duplicate nodes are not added).'),
                ('merge','Merge (Duplicate nodes properties are merged).'),
                ("duplicate",'Duplicate (Duplicate Nodes are added to the graph).'),
                ('overwrite','Overwrite (New nodes overwrite older duplicate nodes).')]
                
class UploadForm(FlaskForm):
    class Meta:
        csrf = False
    submit_upload = SubmitField('Submit')
    upload  = FileField('Upload File',validators=[validators.InputRequired()])
    
class PasteForm(FlaskForm):
    class Meta:
        csrf = False
    submit_paste = SubmitField('Submit')
    paste = TextAreaField('Paste',validators=[validators.InputRequired()])

class UploadGraphForm(UploadForm):
    class Meta:
        csrf = False
    file_type = SelectField("Datatype",choices=graph_choices)
    graph_name = TextAreaField('Graph Name (Optional)')
    mode = SelectField("Integration Mode",choices=mode_choices)

class PasteGraphForm(PasteForm):
    class Meta:
        csrf = False
    file_type = SelectField("Datatype",choices=graph_choices)
    graph_name = TextAreaField('Graph Name (Optional)')
    mode = SelectField("Integration Mode",choices=mode_choices)

class SynbioGraphForm(FlaskForm):
    class Meta:
        csrf = False
    submit_sbh = SubmitField('Submit')
    pmid = TextAreaField('ID',validators=[validators.InputRequired()])
    graph_name = TextAreaField('Graph Name (Optional)')
    mode = SelectField("Integration Mode",choices=mode_choices)

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

def add_remove_graph_form(choices,**kwargs):
    class RemoveGraphForm(FlaskForm):
        class Meta:
            csrf = False
        submit = SubmitField('Remove')
    setattr(RemoveGraphForm, "graphs",SelectField("Graph Name",choices=[(c,c) for c in choices])) 
    return RemoveGraphForm(**kwargs)


