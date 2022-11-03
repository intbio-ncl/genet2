import os
from datetime import datetime
from urllib.parse import urlparse
from werkzeug.utils import secure_filename

def handle_upload(form,sess_dir,file_type=None):
    file_data = form.upload.data
    if form.file_type.data == "SBOL":
        suffix = ".xml"
    else:
        suffix = ".gbk"
    filename = file_data.filename
    filename = secure_filename(filename)
    secure_fn = os.path.join(sess_dir,filename)
    file_data.save(secure_fn)
    if hasattr(form,"graph_name") and form.graph_name.data != "":
        gn = form.graph_name.data 
        secure_fn_n = os.path.join(sess_dir,gn+suffix)
        os.rename(secure_fn,secure_fn_n) 
        secure_fn = secure_fn_n
    else: 
        gn = filename.split(".")[0]
    return secure_fn,gn

def handle_paste(form,sess_dir):
    if form.file_type.data == "SBOL":
        suffix = ".xml"
    else:
        suffix = ".gbk"

    if form.graph_name.data != "":
        gn = form.graph_name.data 
    else: 
        gn = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = os.path.join(sess_dir,f'{gn}{suffix}')
    with open(filename,"a+") as f:
        f.write(form.paste.data)
    return filename,gn

def handle_synbiohub(form,sess_dir,connector):
    identifier = form.pmid.data
    if _uri_validator(identifier):
        identifier = identifier.split("/")[-2]

    if form.graph_name.data != "":
        gn = form.graph_name.data 
    else: 
        gn = identifier

    filename = os.path.join(sess_dir,gn + ".xml")
    try:
        connector.get(identifier,output=filename)
    except ValueError:
        return None
    return filename,gn

def _uri_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc])
    except:
        return False