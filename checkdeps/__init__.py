import logging
from .dep_check import getDeps
import json

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:

    result = "ERROR!"
    if "name" in req.params and "version" in req.params:
        result = getDeps(
            package=req.params.get("name"), version=req.params.get("version")
        )
    elif "name" in req.params:
        result = getDeps(package=req.params.get("name"))
    else:
        return func.HttpResponse("Invalid arguments passed", status_code=400)

    return func.HttpResponse(json.dumps([result]))
