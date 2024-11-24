from flask import Blueprint, render_template, request, abort

from .user_manager import get_similar_users
from .tag_manager import get_similar_tags

bp = Blueprint('search', __name__)

@bp.route('/search')
def search():
    seach_term = request.args.get('query', None ,type=str)

    if not seach_term:
        abort(404, description="You need to be searching something.")

    users = get_similar_users(seach_term)
    tags = get_similar_tags(seach_term)

    return render_template('search.html', seach_term=seach_term, users=users, tags=tags)