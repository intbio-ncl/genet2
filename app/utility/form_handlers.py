import os
from datetime import datetime
from urllib.parse import urlparse
from werkzeug.utils import secure_filename

def handle_upload(form,sess_dir):
    file_data = form.upload.data
    file_type = form.file_type.data
    filename = f'{file_data.filename.split(".")[0]}.{file_type}'
    filename = secure_filename(filename)
    secure_fn = os.path.join(sess_dir,filename)
    file_data.save(secure_fn)
    return secure_fn

def handle_paste(form,sess_dir):
    filename = datetime.now().strftime("%Y%m%d-%H%M%S")
    file_type = form.file_type.data
    filename = os.path.join(sess_dir,f'{filename}.{file_type}')

    with open(filename,"a+") as f:
        f.write(form.paste.data)
    return filename

def handle_synbiohub(form,sess_dir,connector):
    identifier = form.pmid.data
    if _uri_validator(identifier):
        identifier = identifier.split("/")[-2]
    filename = os.path.join(sess_dir,identifier + ".xml")
    try:
        connector.get(identifier,output=filename)
    except ValueError:
        return None
    return filename

def _uri_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc])
    except:
        return False