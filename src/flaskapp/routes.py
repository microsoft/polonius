

from flask import Blueprint, render_template, request

from src.flaskapp.db_operations import generate_uuid, saveTriageNote, saveTriagePage

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

# @bp.get("/api/test/notes")
# def notes_test():
#     return process_test_notes()
