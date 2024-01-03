"""App exceptions."""

from connexion.exceptions import (  # type: ignore
    BadRequestProblem,
    ExtraParameterProblem,
    Forbidden,
    Unauthorized,
)
from pydantic import ValidationError
from pymongo.errors import PyMongoError  # type: ignore
from werkzeug.exceptions import (
    BadRequest,
    InternalServerError,
    NotFound,
)


class EngineProblem(InternalServerError):
    """The external workflow engine appears to experience problems."""


class EngineUnavailable(EngineProblem):
    """The external workflow engine is not available."""


class NoSuitableEngine(BadRequest):
    """No suitable workflow engine known."""


class RunNotFound(NotFound):
    """Workflow run with given identifier not found."""


class IdsUnavailableProblem(PyMongoError):
    """No unique run identifier available."""


class StorageUnavailableProblem(OSError):
    """Storage unavailable for OS operations."""


exceptions = {
    Exception: {
        "message": "An unexpected error occurred.",
        "code": "500",
    },
    BadRequest: {
        "message": "The request is malformed.",
        "code": "400",
    },
    BadRequestProblem: {
        "message": "The request is malformed.",
        "code": "400",
    },
    ExtraParameterProblem: {
        "message": "The request is malformed.",
        "code": "400",
    },
    NoSuitableEngine: {
        "message": "No suitable workflow engine known.",
        "code": "400",
    },
    ValidationError: {
        "message": "The request is malformed.",
        "code": "400",
    },
    Unauthorized: {
        "message": " The request is unauthorized.",
        "code": "401",
    },
    Forbidden: {
        "message": "The requester is not authorized to perform this action.",
        "code": "403",
    },
    NotFound: {
        "message": "The requested resource wasn't found.",
        "code": "404",
    },
    RunNotFound: {
        "message": "The requested run wasn't found.",
        "code": "404",
    },
    EngineUnavailable: {
        "message": "Could not reach remote WES service.",
        "code": "500",
    },
    InternalServerError: {
        "message": "An unexpected error occurred.",
        "code": "500",
    },
    IdsUnavailableProblem: {
        "message": "No/few unique run identifiers available.",
        "code": "500",
    },
    StorageUnavailableProblem: {
        "message": "Storage is not accessible.",
        "code": "500",
    },
}
