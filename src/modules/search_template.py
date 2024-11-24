from flask import Blueprint, render_template

bp = Blueprint('search', __name__)

@bp.route('/search')
def search():
    return render_template('search.html')