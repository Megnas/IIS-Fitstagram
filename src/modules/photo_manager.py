import base64
import string
from uuid import uuid5
from werkzeug.utils import secure_filename

from .db import db, Photo
from flask import Request, flash

def render_picture(data):
    render_pic = base64.b64encode(data).decode('ascii')
    return render_pic

def upload_image(file):
    data = file.read()
    name = secure_filename(file.filename)
    mimetype = file.mimetype
    new_photo = Photo(name=name, data=data,mimetype=mimetype)
    db.session.add(new_photo)
    db.session.commit()

def get_pic_by_id(id: int):
    img = Photo.query.filter_by(id=id).first() # TODO placeholder image
    return img