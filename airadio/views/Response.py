import json
import time


def GenericResponse(meta={},result={},error={}):

    if not error:
        error = {"code": 0,
                 "description": "successful"}
    response = {"meta": meta,
                "result": result,
                "error": error}
    return response
