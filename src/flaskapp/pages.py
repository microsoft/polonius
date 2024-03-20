import asyncio

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

    input_data = models.TriageNote(
        mrn=data.get("MRN"), stat=data.get("STAT"), age=data.get("Age"), sex=data.get("Sex"), 
        triage=data.get("Triage"), correlation_id=correlation_id
    )
    input_data.save()

    kernel = helpers.KernelFactory.create_kernel()

    running_text_sk_function = kernel.plugins["TriagePlugin"]["Notes"]
    running_text_args = KernelArguments(input=str(data.get("Triage")))

    # Flask does not natively support async functions, so we need to create a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(kernel.invoke(running_text_sk_function, running_text_args))
        pager_response = models.TriagePage(correlation_id=correlation_id, page=str(result))
        pager_response.save()
        return str(result)
    except Exception as e:
        return str(e)
    finally:
        loop.close()
