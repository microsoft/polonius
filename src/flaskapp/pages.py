import asyncio
from contextlib import closing

from flask import Blueprint, render_template, request
from semantic_kernel.functions.kernel_arguments import KernelArguments

from . import helpers, models

bp = Blueprint("pages", __name__)


@bp.get("/")
def index():
    return render_template("index.html")


@bp.post("/api/notes")
def notes():
    data = request.get_json()

    # create a UUID for the correlation_id
    correlation_id = helpers.generate_uuid()

    Triage = data.get("Triage")
    max_limit = data.get("max_limit")

    kernel = helpers.KernelFactory.create_kernel()

    triage_sk_function = kernel.plugins["TriagePlugin"]["Notes"]
    triage_sk_args = KernelArguments(input=str(Triage), max_limit=max_limit)

    # Flask does not natively support async functions, so we need to create a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    input_data = models.TriageNote(
        pid=data.get("MRN"),
        stat=data.get("STAT"),
        age=data.get("Age"),
        sex=data.get("Sex"),
        triage=data.get("Triage"),
        correlation_id=correlation_id,
    )

    db_result_input = save_to_db(input_data)
    if db_result_input and "Error" in db_result_input:
        return db_result_input

    result = invoke_sk_function(loop, kernel, triage_sk_function, triage_sk_args)
    if result and "Error" in result:
        return result

    pager_text = result.get_inner_content().choices[0].message.content

    pager_response = models.TriagePage(correlation_id=correlation_id, page=pager_text)

    db_result_pager = save_to_db(pager_response)
    if db_result_pager and "Error" in db_result_pager:
        return db_result_pager

    return str(result)


def invoke_sk_function(loop, kernel, sk_function, sk_function_args):
    # refactored loop.close() with a context manager
    try:
        with closing(loop):
            return loop.run_until_complete(kernel.invoke(sk_function, sk_function_args))
    except Exception as e:
        return f"Error invoking semantic function: {str(e)}"


def save_to_db(collection: models):
    try:
        # pager_response = models.TriagePage(correlation_id=correlation_id, page=result)
        collection.save()
    except Exception as e:
        return f"Error saving to database: {str(e)}"
