import base64
import string
from uuid import uuid5
from werkzeug.utils import secure_filename
from PIL import Image
from io import BytesIO
import warnings

from .db import db, Photo
from flask import Request, flash

def render_picture(data):
    render_pic = base64.b64encode(data).decode('ascii')
    return render_pic

def upload_image_to_webg(file, quality: int = 90) -> int:
    image = Image.open(file)
    img_io = BytesIO()
    image.save(img_io, 'WEBP', quality=quality)
    img_io.seek(0)
    name = secure_filename(file.filename.rsplit('.', 1)[0] + '.webp')
    mimetype = 'image/webp'

    new_photo = Photo(name=name, data=img_io.read(), mimetype=mimetype)
    try:
        db.session.add(new_photo)
        db.session.commit()
    except:
        db.session.rollback()
        return None

    return new_photo.id

def upload_image_to_webg_resized(file, quality: int = 60, pheight: int =256, pwidth=256) -> int:
    image = Image.open(file)

    original_width, original_height = image.size
    if original_width > pwidth or original_height > pheight:
        image.thumbnail((pwidth, pheight))

    img_io = BytesIO()
    image.save(img_io, 'WEBP', quality=quality)
    img_io.seek(0)
    name = secure_filename(file.filename.rsplit('.', 1)[0] + '.webp')
    mimetype = 'image/webp'

    new_photo = Photo(name=name, data=img_io.read(), mimetype=mimetype)
    try:
        db.session.add(new_photo)
        db.session.commit()
    except:
        db.session.rollback()
        return None

    return new_photo.id

def upload_image(file) -> int:
    warnings.warn(
        "upload_image() is deprecated and will be removed in future versions.",
        category=DeprecationWarning,
        stacklevel=2
    )
    data = file.read()
    name = secure_filename(file.filename)
    mimetype = file.mimetype
    new_photo = Photo(name=name, data=data,mimetype=mimetype)
    db.session.add(new_photo)
    db.session.commit()
    return new_photo.id

def get_pic_by_id(id: int):
    img = Photo.query.filter_by(id=id).first()
    return img