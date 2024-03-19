#from flask import Blueprint, redirect, render_template, request, url_for
from flask import Blueprint, render_template

#from . import models

bp = Blueprint("pages", __name__)


@bp.get("/")
def index():
    return render_template("index.html")

@bp.get("/api/demo")
def hello_api():
    return {
        "message": "Hello, World!",
    }
