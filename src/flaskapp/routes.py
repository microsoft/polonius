

from flask import Blueprint, render_template, request

from src.flaskapp.db_operations import generate_uuid, saveTriageNote, saveTriagePage
from src.flaskapp.test_notes import process_test_notes

from . import sk_helper

bp = Blueprint("routes", __name__)

@bp.get("/")
def index():
    return render_template("index.html")

@bp.get("/api/demo")
def demo():
    return "Hello, World!"

@bp.post("/api/notes")
def notes():
    data = request.get_json()

    # create a UUID for the correlation_id
    correlation_id = generate_uuid()
    data["correlation_id"] = correlation_id
    saveTriageNote(data)

    kernel = sk_helper.KernelFactory.create_kernel()
    result = sk_helper.execute_kernel_function(kernel, data, "TriagePlugin", "Notes")

    pager_text = result.get_inner_content().choices[0].message.content
    saveTriagePage(correlation_id, pager_text)

    return str(result)


@bp.get("/api/test/notes")
def notes_test():
    skip = request.args.get('skip', default=0, type=int)
    take = request.args.get('take', default=10, type=int)
    max_value = request.args.get('max_value', default=200, type=int)

    return process_test_notes(max_value, skip, take)

@bp.post("/api/iss")
def iss():
    data = request.get_json()

    kernel = sk_helper.KernelFactory.create_kernel()
    result = sk_helper.execute_kernel_function(kernel, data, "TriagePlugin", "ISS")

    return str(result)