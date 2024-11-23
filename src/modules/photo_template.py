from flask import Blueprint, send_file, abort
from flask_login import current_user
import io

from .user_manager import get_user
from .photo_manager import get_pic_by_id
from .groups_manager import get_group

bp = Blueprint('foto', __name__)

@bp.route('/user_image/<int:user_id>')
def get_user_image(user_id):
    user = get_user(user_id)
    if(user):
        if(user.photo_id):
            image = get_pic_by_id(user.photo_id)
            if(image):
                #Return image
                return send_file(
                    io.BytesIO(image.data),
                    mimetype=image.mimetype,
                    as_attachment=False,
                    download_name=image.name
                )
            else:
                #Return error missing image
                abort(404, description="Image data not found.")
        else:
            #Return place holder
            return send_file("static/images/user_placeholder.jpg", mimetype="image/jpg")
    else:
        #Return error non-existent user
        abort(404, description="User does not exists.")

@bp.route('/group_image/<int:group_id>')
def get_group_image(group_id):
    group = get_group(group_id)

    if not group.visibility:
        if not current_user.is_authenticated:
            abort(401, description="Not authorized!")

    if group:
        if(group.photo_id):
            image = get_pic_by_id(group.photo_id)
            if(image):
                #Return image
                return send_file(
                    io.BytesIO(image.data),
                    mimetype=image.mimetype,
                    as_attachment=False,
                    download_name=image.name
                )
            else:
                #Return error missing image
                abort(404, description="Image data not found.")
        else:
            #Return place holder
            return send_file("static/images/user_placeholder.jpg", mimetype="image/jpg")
    else:
        #Return error non-existent group
        abort(404, description="Group does not exists.")