class States:
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
