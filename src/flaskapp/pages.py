#from flask import Blueprint, redirect, render_template, request, url_for
from semantic_kernel.functions.kernel_arguments import KernelArguments
from flask import Blueprint, render_template, request
import os
import logging
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from . import helpers

bp = Blueprint("pages", __name__)


@bp.get("/")
def index():
    return render_template("index.html")

@bp.post("/api/notes")
async def notes():
    data = request.get_json()

    MRN = data.get('MRN')
    STAT = data.get('STAT')
    Age = data.get('Age')
    Sex = data.get('Sex')
    Triage = data.get('Triage')

    kernel = helpers.KernelFactory.create_kernel()

    running_text_sk_function = kernel.plugins["TriagePlugin"]["Notes"]
    running_text_args = KernelArguments(input=str(Triage))
    try:
        result = await kernel.invoke(running_text_sk_function, running_text_args)    
    except Exception as e:
        print(e)
    return str(result)


# class KernelFactory:
#     @staticmethod
#     def create_kernel() -> sk.Kernel:
#         kernel = sk.Kernel()

#         deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
#         api_key = os.getenv('AZURE_OPENAI_API_KEY') 
#         endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
#         script_directory = os.path.dirname(__file__)
#         plugins_directory = os.path.join(script_directory, "plugins")
#         service_id=None
        
#         plugin_names = [plugin for plugin in os.listdir(plugins_directory) if os.path.isdir(os.path.join(plugins_directory, plugin))]
        
       
#         # for each plugin, add the plugin to the kernel
#         try:
#             for plugin_name in plugin_names:
#                 kernel.import_plugin_from_prompt_directory(plugins_directory, plugin_name)
#         except ValueError as e:
#             logging.exception(f"Plugin {plugin_name} not found")
            
#         #add the chat service
#         service = AzureChatCompletion(
#               service_id=service_id,
#               deployment_name=deployment,
#               endpoint=endpoint,
#               api_key=api_key
#             #   api_version="2024-02-15-preview"
#         )

#         kernel.add_service(service)

#         return kernel
    
#     def __str__(self):
#             return self.name