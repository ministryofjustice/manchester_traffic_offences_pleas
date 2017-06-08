from django.core.exceptions import ValidationError


class BadRequestException(ValidationError):
    """
    General 400 casues by validation failure in a request. Will cause a 400
    response to be returned in middleware.
    """

    def __init__(self, message):
        self.message = message
        super(BadRequestException, self).__init__(message)
