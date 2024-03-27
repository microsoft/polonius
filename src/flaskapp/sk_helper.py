import asyncio
import logging
import os
from contextlib import closing

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion


def invoke_sk_function(loop, kernel, sk_function, sk_function_args):
    # refactored loop.close() with a context manager
    try:
        with closing(loop):
            return loop.run_until_complete(kernel.invoke(sk_function, sk_function_args, temperature=0.5))
    except Exception as e:
        return f"Error invoking semantic function: {str(e)}"

def execute_kernel_function(kernel, data, plugin_folder, plugin):
    try:
        triage_sk_function = kernel.plugins[plugin_folder][plugin]
        triage_sk_args = sk.KernelArguments(
                            input=data.get("Triage"), 
                            age=data.get("Age"), 
                            sex=data.get("Sex"), 
                            max_limit=data.get("max_limit"))

        # Flask does not natively support async functions, so we need to create a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        result = invoke_sk_function(loop, kernel, triage_sk_function, triage_sk_args)
        return result
    except Exception as e:
        raise e

class KernelFactory:
    @staticmethod
    def create_kernel() -> sk.Kernel:
        kernel = sk.Kernel()

        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        script_directory = os.path.dirname(__file__)
        plugins_directory = os.path.join(script_directory, "plugins")

        service_id = None

        plugin_names = [
            plugin for plugin in os.listdir(plugins_directory) if os.path.isdir(os.path.join(plugins_directory, plugin))
        ]

        # for each plugin, add the plugin to the kernel
        try:
            for plugin_name in plugin_names:
                kernel.import_plugin_from_prompt_directory(plugins_directory, plugin_name)
        except ValueError:
            logging.exception(f"Plugin {plugin_name} not found")

        # add the chat service
        service = AzureChatCompletion(
            service_id=service_id,
            deployment_name=deployment,
            endpoint=endpoint,
            api_key=api_key,
            #   api_version="2024-02-15-preview"
        )

        kernel.add_service(service)

        return kernel

    def __str__(self):
        return self.name
