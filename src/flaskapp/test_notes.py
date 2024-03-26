import asyncio
import csv

from semantic_kernel.functions.kernel_arguments import KernelArguments

from . import sk_helper


def process_test_notes(max_limit: int = 200, skip: int = 0, take: int = 10):
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
    
    kernel = sk_helper.KernelFactory.create_kernel()

    running_text_sk_function = kernel.plugins["TriagePlugin"]["Notes"]
    updated_data = {}
    first_amount = {k: data[k] for k in list(data)[skip:take]}
    count_down = take - skip
    for key, value in first_amount.items():
        print('Remaining:', count_down)
        count_down -= 1
        running_text_args = KernelArguments(input=value.get("Triage"), age=value.get("Age"), sex=value.get("Sex"),
                                             max_limit=max_limit)
        
        # Flask does not natively support async functions, so we need to create a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = sk_helper.invoke_sk_function(loop, kernel, running_text_sk_function, running_text_args)
    
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
        

    with open('flaskapp/data/results.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(["PID", "STAT", "Age", "Sex", "Triage", "ISS", "Page", "AIPage"])
        for key, value in updated_data.items():
            writer.writerow([value.get("PID"), value.get("STAT"), value.get("Age"), value.get("Sex"), 
                             value.get("Triage"), value.get("ISS"), value.get("Page"), value.get("AIPage")])
       

    return "Done"