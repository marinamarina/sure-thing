from flask import render_template
from flask_login import current_user
from . import main

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('custom_errors/404.html', user=current_user), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('custom_errors/500.html', user=current_user), 500

@main.app_errorhandler(403)
def forbidden_access(e):
    return render_template('custom_errors/403.html', user=current_user), 403
