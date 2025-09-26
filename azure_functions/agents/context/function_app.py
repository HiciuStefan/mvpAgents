import azure.functions as func
import logging
from main_individual import main

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name(name="ContextAgent")
@app.route(route="run-context-agent")
def context_agent_http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP-triggered function to run the context analysis agent.
    """
    logging.info('Python HTTP trigger function processed a request.')

    try:
        main()
        return func.HttpResponse(
                 "Context analysis agent ran successfully.",
                 status_code=200
        )
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return func.HttpResponse(
                 f"An error occurred: {e}",
                 status_code=500
        )
