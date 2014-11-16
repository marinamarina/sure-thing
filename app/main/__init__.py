from flask.blueprints import Blueprint

main = Blueprint('main', __name__, template_folder='templates')

from . import views, errors