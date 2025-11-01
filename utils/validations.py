from exceptions.custom_exceptions import MissingOrInvalidEnvironmentVariableError


def validate_env_vars(**kwargs):
    missing = [name for name, value in kwargs.items() if not value]
    if missing:
        raise MissingOrInvalidEnvironmentVariableError(missing)
