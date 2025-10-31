from functools import wraps
from flask import session, flash, redirect, url_for

def role_required(required_role):
    """Generic decorator to check session role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get("role") != required_role:
                flash(f"Unauthorized access. Please log in as {required_role}.", "danger")
                return redirect(url_for("login"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Specific role decorators for convenience
traveller_required = role_required("tourist")
provider_required = role_required("provider")
admin_required = role_required("admin")
