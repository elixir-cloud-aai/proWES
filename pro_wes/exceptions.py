from connexion.exceptions import (
    BadRequestProblem,
    ExtraParameterProblem,
    Forbidden,
    Unauthorized,
)

from werkzeug.exceptions import (
    BadRequest,
    InternalServerError,
    NotFound,
)


class RunNotFound(NotFound):
    """Raised when workflow run with given run identifier was not found."""
    pass


class ValidationError(ValueError):
    """Raised when an object does not conform to a schema."""
    pass


exceptions = {
    Exception: {
        "message": "An unexpected error occurred.",
        "code": '500',
    },
    BadRequestProblem: {
        "message": "The request is malformed.",
        "code": '400',
    },
    BadRequest: {
        "message": "The request is malformed.",
        "code": '400',
    },
    ExtraParameterProblem: {
        "message": "The request is malformed.",
        "code": '400',
    },
    Unauthorized: {
        "message": " The request is unauthorized.",
        "code": '401',
    },
    Forbidden: {
        "message": "The requester is not authorized to perform this action.",
        "code": '403',
    },
    NotFound: {
        "message": "The requested resource wasn't found.",
        "code": '404',
    },
    RunNotFound: {
        "message": "The requested run wasn't found.",
        "code": '404',
    },
    ValidationError: {
        "message": "The object does not conform to the schema.",
        "code": '500',
    },
    InternalServerError: {
        "message": "An unexpected error occurred.",
        "code": '500',
    },
}
