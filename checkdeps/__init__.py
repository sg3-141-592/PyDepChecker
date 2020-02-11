from .dep_check import getDeps
import json

import azure.functions as func

# Override json serialiser behaviour to return sets
def json_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

def main(req: func.HttpRequest) -> func.HttpResponse:

    result = "ERROR!"
    if "name" in req.params:
        result = getDeps(package=req.params.get("name"))
    else:
        return func.HttpResponse("Invalid arguments passed", status_code=400)

    return func.HttpResponse(json.dumps([result], default=json_default))
