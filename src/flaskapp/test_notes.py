import asyncio
import csv

from semantic_kernel.functions.kernel_arguments import KernelArguments
from tqdm import tqdm

from . import sk_helper


def process_test_notes(src_file: str, dest_file: str, max_limit: int = 200, start: int = 0, end: int = 10):
    data = {}
    with open(src_file) as file:
        csv_reader = csv.DictReader(file)
        for i, row in enumerate(csv_reader):
            data[i] ={
                "MRN": row["MRN_hashed"],
                "STAT": row["STAT"],
                "Age": row["Age"],
                "Sex": row["Sex"],
                "Triage": row["triageText"],
                "Page" : row["Page"],
                "ISS": row["ISS"]
            }
        
    
    kernel = sk_helper.KernelFactory.create_kernel()

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
            loop.run_until_complete(asyncio.sleep(1))  # wait for 1 second
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
        

    with open(dest_file, 'w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(["PID", "STAT", "Age", "Sex", "Triage", "ISS", "Page", "AIPage"])
        for key, value in updated_data.items():
            writer.writerow([value.get("PID"), value.get("STAT"), value.get("Age"), value.get("Sex"), 
                             value.get("Triage"), value.get("ISS"), value.get("Page"), value.get("AIPage")])
       

    return "Done"