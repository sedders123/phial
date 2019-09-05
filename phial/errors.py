"""phial's custom errors."""


class ArgumentValidationError(Exception):
    """Exception indicating argument validation has failed."""

    pass


class ArgumentTypeValidationError(ArgumentValidationError):
    """Exception indicating argument type validation has failed."""

    pass
