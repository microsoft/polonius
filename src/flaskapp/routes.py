from flask import Blueprint, render_template, request

from .db_operations import generate_uuid, saveTriageNote, saveTriagePage
from .sk_helper import KernelFactory, execute_kernel_function

#generate_uuid, process_test_notes, saveTriageNote, saveTriagePage, sk_helper

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
    err = saveTriageNote(data)
    if err:
        print(err)

    kernel = KernelFactory.create_kernel()
    result = execute_kernel_function(kernel, data, "TriagePlugin", "Notes")

    pager_text = result.get_inner_content().choices[0].message.content
    err = saveTriagePage(correlation_id, pager_text)
    if err:
        print(err)

    return str(result)
