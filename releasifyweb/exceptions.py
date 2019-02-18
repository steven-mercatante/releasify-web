from falcon import HTTPBadRequest


class JSONBodyRequiredError(HTTPBadRequest):
    def __init__(self):
        msg = 'A valid JSON request body is required'
        super(JSONBodyRequiredError, self).__init__(description=msg)


class MissingRequiredArgError(Exception):
    def __init__(self, arg):
        message = f'You\'re missing the required `{arg}` argument'
        super(MissingRequiredArgError, self).__init__(message)
