from flask import Blueprint, send_file, abort, render_template
from flask_login import current_user
import io

from .db import Post

from .user_manager import get_user
from .photo_manager import get_pic_by_id
from .groups_manager import get_group
from .post_manager import get_post_by_id, can_see_post, get_post_by_id

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

    if group:
        if not group.visibility:
            if not current_user.is_authenticated:
                abort(401, description="Not authorized!")
            if not (current_user.id == group.owner_id or current_user.id in group.users):
                abort(401, description="Not authorized!")

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

@bp.route('/post_image/<int:post_id>')
def get_post_image(post_id):
    post: Post = get_post_by_id(post_id)
    if post:
        if not post.visibility:
            if not current_user.is_authenticated:
                abort(401, description="Not authorized!")
            if not can_see_post(current_user, post):
                abort(401, description="Not authorized!")
        
        if(post.photo_id):
            image = get_pic_by_id(post.photo_id)
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
        abort(404, description="Post does not exists.")
