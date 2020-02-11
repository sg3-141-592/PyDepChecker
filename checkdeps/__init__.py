from .dep_check import getDeps
import json

import azure.functions as func

# Override json serialiser behaviour to return sets
def json_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

def main(req: func.HttpRequest) -> func.HttpResponse:
    requestData = req.get_json()
    if 'data' in requestData:
        result = getDeps(requestData['data'])
        return func.HttpResponse(json.dumps(result, default=json_default), status_code=200)
    else:
        return func.HttpResponse("Invalid arguments passed", status_code=400)
