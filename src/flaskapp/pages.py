import asyncio
import csv
from contextlib import closing

from flask import Blueprint, render_template, request
from semantic_kernel.functions.kernel_arguments import KernelArguments
from tqdm import tqdm

from . import helpers, models

bp = Blueprint("pages", __name__)


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
    correlation_id = helpers.generate_uuid()

    Triage = data.get("Triage")
    max_limit = data.get("max_limit")

    kernel = helpers.KernelFactory.create_kernel()

    triage_sk_function = kernel.plugins["TriagePlugin"]["Notes"]
    triage_sk_args = KernelArguments(input=str(Triage), age=data.get("Age"), sex=data.get("Sex"), max_limit=max_limit)
    
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
            return loop.run_until_complete(kernel.invoke(sk_function, sk_function_args, temperature=0.5))
    except Exception as e:
        return f"Error invoking semantic function: {str(e)}"


def save_to_db(collection: models):
    try:
        # pager_response = models.TriagePage(correlation_id=correlation_id, page=result)
        collection.save()
    except Exception as e:
        return f"Error saving to database: {str(e)}"


@bp.get("/api/test/notes")
def notes_test():
    start = request.args.get('start', default=0, type=int)
    end = request.args.get('end', default=10, type=int)
    max_limit = request.args.get('max_limit', default=200, type=int)

    data = {}
    with open('src/flaskapp/data/testpages.csv') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            data[row[0]] ={
                "MRN": row[1],
                "STAT": row[2],
                "Age": row[3],
                "Sex": row[4],
                "Triage": row[5],
                "Page" : row[6],
                "ISS": row[7]
            }
        
    #remove the header
    items = list(data.items())
    del items[0]
    data = dict(items)
    
    kernel = helpers.KernelFactory.create_kernel()

    running_text_sk_function = kernel.plugins["TriagePlugin"]["Notes"]
    updated_data = {}

    first_amount = {k: data[k] for k in list(data)[start:end]}
    
    for key, value in tqdm(first_amount.items(), total=len(first_amount), desc="Processing"):
        running_text_args = KernelArguments(input=value.get("Triage"), age=value.get("Age"), sex=value.get("Sex"),
                                             max_limit=max_limit)
        
        # Flask does not natively support async functions, so we need to create a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = invoke_sk_function(loop, kernel, running_text_sk_function, running_text_args)
    
            updated_data[key] = {
                "PID": value.get("MRN"),
                "STAT": value.get("STAT"),
                "Age": value.get("Age"),
                "Sex": value.get("Sex"),
                "Triage": value.get("Triage"),
                "ISS": value.get("ISS"),
                "Page" : value.get("Page"),
                "AIPage": str(result)
            } 
        except Exception as e:
            return str(e)
        finally:
            loop.close()
        

    with open('src/flaskapp/data/results.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(["PID", "STAT", "Age", "Sex", "Triage", "ISS", "Page", "AIPage"])
        for key, value in updated_data.items():
            writer.writerow([value.get("PID"), value.get("STAT"), value.get("Age"), value.get("Sex"), 
                             value.get("Triage"), value.get("ISS"), value.get("Page"), value.get("AIPage")])
       

    return "Done"