import asyncio
import csv

from flask import Blueprint, render_template, request
from semantic_kernel.functions.kernel_arguments import KernelArguments

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
    
    input_data = models.TriageNote(
        mrn=data.get("MRN"), stat=data.get("STAT"), age=data.get("Age"), sex=data.get("Sex"), 
        triage=data.get("Triage"), correlation_id=correlation_id
    )
    input_data.save()

    kernel = helpers.KernelFactory.create_kernel()

    running_text_sk_function = kernel.plugins["TriagePlugin"]["Notes"]
    running_text_args = KernelArguments(
        input=f'{data.get("Triage")} STAT={data.get("STAT")} Age={data.get("Age")} Sex={data.get("Sex")}')

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


@bp.get("/api/test/notes")
def notes_test():

    data = {}
    with open('flaskapp/data/testpages.csv') as file:
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

    first_amount = {k: data[k] for k in list(data)[:10]}
  
    for key, value in first_amount.items():
        running_text_args = KernelArguments(
            input=f'{value.get("Triage")} STAT={value.get("STAT")} Age={value.get("Age")} Sex={value.get("Sex")}')

        # Flask does not natively support async functions, so we need to create a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(kernel.invoke(running_text_sk_function, running_text_args))
            
            updated_data[key] = {
                "MRN": value.get("MRN"),
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
        

    with open('flaskapp/data/results.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(["MRN", "STAT", "Age", "Sex", "Triage", "ISS", "Page", "AIPage"])
        for key, value in updated_data.items():
            writer.writerow([value.get("MRN"), value.get("STAT"), value.get("Age"), value.get("Sex"), 
                             value.get("Triage"), value.get("ISS"), value.get("Page"), value.get("AIPage")])
       

    return "Done"