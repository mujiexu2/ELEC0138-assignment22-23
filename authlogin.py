# -*- coding: utf-8 -*-
# Implement login restriction, some pages can only be accessed after logging in
# Implement by defining a decorator

from functools import wraps
from flask import session, redirect, url_for


def login_required(func):
    @wraps(func)  # Prevent some signatures of the incoming function from being lost.
    def wrapper(*args, **kwargs):
        if session.get("email"):
            # Currently logged in
            print(session.get('email'))
            return func(*args, **kwargs)
        else:
            return redirect(url_for("login"))

    return wrapper

