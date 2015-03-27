import functools

from flask import abort
from flask import request, render_template
from flask_login import current_user

from .models import Permission

# a decorator that would check if
# a user has required permissions for this route,
# otherwise redirect to 403
def permission_required(permission):
    def actual_decorator(function):
        @functools.wraps(function)
        def decorated_function(*args):
            if not current_user.can(permission):
                return abort(403)
            return function(*args)
        return decorated_function
    return actual_decorator


def admin_required():
    return permission_required(Permission.ADMINISTER)

# a decorator that would allow a route to render a template
# source: flask documentation, http://flask.pocoo.org/docs/0.10/patterns/viewdecorators/
def templated(template=None):
    def decorator(function):
        @functools.wraps(function)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = request.endpoint \
                    .replace('.', '/') + '.html'
            ctx = function(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                return ctx
            return render_template(template_name, **ctx)
        return decorated_function
    return decorator