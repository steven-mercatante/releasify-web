from falcon import HTTPBadRequest


class JSONBodyRequiredError(HTTPBadRequest):
    def __init__(self):
        msg = 'A JSON request body is required'
        super(JSONBodyRequiredError, self).__init__(description=msg)
