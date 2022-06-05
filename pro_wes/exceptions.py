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


exceptions = {
    Exception: {
        "msg": "An unexpected error occurred.",
        "status_code": '500',
    },
    BadRequestProblem: {
        "msg": "The request is malformed.",
        "status_code": '400',
    },
    BadRequest: {
        "msg": "The request is malformed.",
        "status_code": '400',
    },
    ExtraParameterProblem: {
        "msg": "The request is malformed.",
        "status_code": '400',
    },
    Unauthorized: {
        "msg": " The request is unauthorized.",
        "status_code": '401',
    },
    Forbidden: {
        "msg": "The requester is not authorized to perform this action.",
        "status_code": '403',
    },
    NotFound: {
        "msg": "The requested resource wasn't found.",
        "status_code": '404',
    },
    RunNotFound: {
        "msg": "The requested run wasn't found.",
        "status_code": '404',
    },
    InternalServerError: {
        "msg": "An unexpected error occurred",
        "status_code": '500',
    },
}
