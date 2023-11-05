"""WES run states."""

# pragma pylint: disable=too-few-public-methods


class States:
    """WES run states."""

    UNDEFINED = [
        "UNKNOWN",
    ]

    CANCELABLE = [
        "INITIALIZING",
        "PAUSED",
        "QUEUED",
        "RUNNING",
    ]

    FINISHED = [
        "COMPLETE",
        "EXECUTOR_ERROR",
        "SYSTEM_ERROR",
        "CANCELED",
    ]

    UNFINISHED = CANCELABLE + [
        "CANCELING",
    ]

    ALL = FINISHED + UNFINISHED + UNDEFINED
